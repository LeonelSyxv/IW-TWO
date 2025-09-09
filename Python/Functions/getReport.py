import sys, os, json
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Database.db import get_connection

def get_report():
    try:
        conn = get_connection()

        with conn.cursor() as cursor:
            query = """
              SELECT
                c.number,
                c.name,
                rd.description,
                rd.protocol,
                rd.media,
                s.name AS stage_name
              FROM reports r
              JOIN report_details rd ON rd.report_id = r.id
              JOIN channels c ON c.id = rd.channel_id
              JOIN stages s ON s.id = rd.stage_id
              WHERE r.status = 'Revision' AND r.type = 'Momentary'
              ORDER BY s.name, c.number
            """
            cursor.execute(query)
            results = cursor.fetchall()

            if not results:
                return ["✅ *No se han detectado fallos momentáneos* en canales actualmente en revisión."]
            
            grouped_by_stage = defaultdict(list)

            for number, name, description, protocol, media, stage in results:
                channel_label = f"*Canal {number} {name}*"
                description = description.strip()

                if protocol or media:
                    issue = f"Problema de *{media}*" if media else "*Sin A/V*"
                    additional = f" ({issue} en *{protocol}*)" if protocol else f" (*{issue}*)"
                else:
                    additional = ""

                grouped_by_stage[stage].append(f"• {channel_label}: {description}{additional}")

            messages = []
            for stage, channel_lines in grouped_by_stage.items():
                sorted_lines = sorted(
                    channel_lines,
                    key=lambda line: int(line.split("*Canal ")[1].split(" ")[0])
                )
                header = f"⚠️ Fallos detectados en *{stage}* *({len(sorted_lines)} Canal{'es' if len(sorted_lines) != 1 else ''})*:"
                body = "\n\n".join(sorted_lines)
                messages.append(f"{header}\n\n{body}")

            return messages

    except Exception as e:
        return [f"[❌ (getReport.py/get_report)] An error occurred while generating the report: {str(e)}"]
    
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    messages = get_report()
    print(json.dumps(messages, ensure_ascii=False), flush=True)