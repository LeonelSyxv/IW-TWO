import sys, os, json, time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Database.db import get_connection

sys.stdout.reconfigure(encoding="utf-8")

def get_resolved_report(poll_interval=30):
    print("Starting watcher for resolved channels...", flush=True)
    previous_revision = {}
    initialized = False

    while True:
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT c.id, c.number, c.name, rd.media, rd.protocol
                    FROM reports r
                    JOIN report_details rd ON rd.report_id = r.id
                    JOIN channels c ON c.id = rd.channel_id
                    WHERE r.status = 'Revision' AND r.type = 'Momentary'
                """)
                current_revision = {
                    row[0]: {
                        "number": row[1],
                        "name": row[2],
                        "media": row[3],
                        "protocol": row[4]
                    }
                    for row in cursor.fetchall()
                }

            if initialized:
                resolved_ids = set(previous_revision.keys()) - set(current_revision.keys())
                messages = []

                for channel_id in resolved_ids:
                    channel = previous_revision[channel_id]
                    number = channel["number"]
                    name = channel["name"]
                    media = channel["media"]
                    protocol = channel["protocol"] or ''

                    messages.append(
                        f"✅ *Canal {number} {name}*: Ya se encuentra operando correctamente "
                        f"con: *{media}* en *{protocol}*."
                    )

                if messages:
                    print(json.dumps(messages, ensure_ascii=False), flush=True)

            else:
                print("First watcher cycle, no messages sent.", flush=True)
                initialized = True

            previous_revision = current_revision

        except Exception as e:
            print(json.dumps([f"[❌ (getResolvedReport.py)] Error: {str(e)}"]), flush=True)

        time.sleep(poll_interval)

if __name__ == "__main__":
    get_resolved_report(poll_interval=15)
