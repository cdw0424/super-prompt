#!/usr/bin/env python3
"""
Simple TCP server for Super Prompt MCP on port 8282
"""
import socket
import threading
import json
import sys
import os

def handle_client(client_socket, addr):
    """Handle individual client connections"""
    print(f"-------- TCP connection from {addr}", file=sys.stderr, flush=True)
    try:
        buffer = ""
        while True:
            data = client_socket.recv(4096)
            if not data:
                break

            buffer += data.decode('utf-8')

            # JSON 메시지 완성 확인 (줄바꿈으로 구분)
            if '\n' in buffer:
                messages = buffer.split('\n')
                buffer = messages[-1]  # 마지막 불완전 메시지 저장

                for msg in messages[:-1]:
                    if msg.strip():
                        try:
                            request = json.loads(msg.strip())
                            # 간단한 MCP 응답
                            response = {
                                "jsonrpc": "2.0",
                                "id": request.get("id"),
                                "result": {
                                    "message": "Super Prompt MCP Server on port 8282",
                                    "tools": ["high", "architect", "dev", "analyzer", "doc-master"],
                                    "version": "4.2.0",
                                    "status": "ready"
                                }
                            }
                            response_json = json.dumps(response) + '\n'
                            client_socket.send(response_json.encode('utf-8'))
                            print(f"-------- TCP response sent to {addr}", file=sys.stderr, flush=True)
                        except json.JSONDecodeError as e:
                            print(f"-------- TCP JSON parse error: {e}", file=sys.stderr, flush=True)
                            continue
    except Exception as e:
        print(f"-------- TCP client error: {e}", file=sys.stderr, flush=True)
    finally:
        client_socket.close()
        print(f"-------- TCP connection closed for {addr}", file=sys.stderr, flush=True)

def main():
    """Main TCP server function"""
    port = 8282

    print(f"-------- Super Prompt TCP Server starting on port {port}", file=sys.stderr, flush=True)

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('127.0.0.1', port))
        server_socket.listen(5)

        print(f"-------- TCP server successfully listening on port {port}", file=sys.stderr, flush=True)
        print(f"-------- Server ready to accept connections", file=sys.stderr, flush=True)

        while True:
            try:
                client_socket, addr = server_socket.accept()
                print(f"-------- Accepting TCP connection from {addr}", file=sys.stderr, flush=True)
                client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
                client_thread.daemon = True
                client_thread.start()
            except KeyboardInterrupt:
                print("-------- TCP server shutting down", file=sys.stderr, flush=True)
                break
            except Exception as e:
                print(f"-------- TCP server error: {e}", file=sys.stderr, flush=True)

        server_socket.close()

    except Exception as e:
        print(f"-------- ERROR: Failed to start TCP server: {e}", file=sys.stderr, flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
