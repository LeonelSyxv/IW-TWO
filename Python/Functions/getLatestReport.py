import sys, os, time, json
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Database.db import get_connection

sys.stdout.reconfigure(encoding="utf-8")

def get_latest_report(poll_interval=30):
    print("Starting watcher for latest channels...", flush=True)
    processed_report_ids = set()
    start_time = None

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT created_at
                FROM reports
                WHERE type = 'Momentary' AND status = 'Revision'
                ORDER BY created_at DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                start_time = row[0]
    except Exception as e:
        print(f"[❌ (getLatestReport.py/get_latest_report)] Error fetching initial report timestamp: {e}", flush=True)

    while True:
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT MAX(updated_at)
                    FROM reports
                    WHERE status = 'Resolved'
                """)
                last_resolved_time = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT id, reviewed_by, created_at
                    FROM reports
                    WHERE type = 'Momentary' AND status = 'Revision'
                    ORDER BY created_at DESC
                    LIMIT 1
                """)
                row = cursor.fetchone()

                if not row:
                    time.sleep(poll_interval)
                    continue

                report_id, reviewed_by, created_at = row

                if start_time and created_at <= start_time:
                    processed_report_ids.add(report_id)
                    time.sleep(poll_interval)
                    continue

                if last_resolved_time and created_at <= last_resolved_time:
                    processed_report_ids.add(report_id)
                    time.sleep(poll_interval)
                    continue

                if report_id in processed_report_ids:
                    time.sleep(poll_interval)
                    continue

                cursor.execute("""
                    SELECT 
                        c.number, 
                        c.name, 
                        rd.description, 
                        rd.protocol, 
                        rd.media, 
                        s.name AS stage_name
                    FROM report_details rd
                    JOIN channels c ON c.id = rd.channel_id
                    JOIN stages s ON s.id = rd.stage_id
                    WHERE rd.report_id = %s
                """, (report_id,))
                results = cursor.fetchall()

                if not results:
                    processed_report_ids.add(report_id)
                    time.sleep(poll_interval)
                    continue

                grouped_by_stage = defaultdict(list)

                for number, name, description, protocol, media, stage in results:
                    desc = description.strip() if description else ""
                    issue = f"Problema de *{media}*" if media else "Sin A/V"
                    additional = f" ({issue} en *{protocol}*)" if protocol else f" ({issue})"
                    grouped_by_stage[stage].append((f"*Canal {number} {name}*", desc + additional))

                messages_to_send = []
                for stage, channel_list in grouped_by_stage.items():
                    sorted_lines = sorted(
                        [f"• {label}: {text}" for label, text in channel_list],
                        key=lambda line: int(line.split("Canal ")[1].split(" ")[0])
                    )
                    if not sorted_lines:
                        continue
                    header = f"⚠️ Nuevos fallos detectados en *{stage}* *({len(sorted_lines)} Canal{'es' if len(sorted_lines) != 1 else ''})*:"
                    body = "\n\n".join(sorted_lines)
                    message = f"{header}\n\n{body}\n\nEn revisión por *{reviewed_by}*."
                    messages_to_send.append(message)

                if messages_to_send:
                    print(json.dumps(messages_to_send, ensure_ascii=False), flush=True)

                processed_report_ids.add(report_id)

        except Exception as e:
            print(f"[❌ (getLatestReport.py/get_latest_report)] Error in watcher loop: {e}", flush=True)

        time.sleep(poll_interval)

if __name__ == "__main__":
    get_latest_report(poll_interval=15)
