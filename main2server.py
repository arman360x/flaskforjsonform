import asyncio
import json
import socket
import aiohttp  # This will be used to make HTTP requests to Flask server

SERVER_PORT = 9090  # Local server for Client 2
SOCKET_HEADER_SIZE = 8
FLASK_SERVER_URL = "http://localhost:5000/send_data"  # Flask server URL

# Function to fetch JSON data from the Flask server (Server 1)
async def fetch_json_data_from_server1():
    try:
        # Use aiohttp to fetch data from Flask server
        async with aiohttp.ClientSession() as session:
            json_data = {"data": '{"key": "value"}'}  # Example data to send in the POST request

            # Send the JSON data to Flask server using POST
            async with session.post(FLASK_SERVER_URL, data=json_data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    print(f"Received response from Flask server: {response_data}")
                    return response_data
                else:
                    print(f"Failed to fetch data. Status code: {response.status}")
                    return None
    except Exception as e:
        print(f"Error fetching data from Flask server: {e}")
        return None

# Function to handle communication with Client 2
async def handle_client(reader, writer):
    try:
        while True:
            # Fetch the latest JSON data from the Flask server
            json_data = await fetch_json_data_from_server1()

            if json_data:
                # Prepare data to send to Client 2
                data_to_send = json.dumps(json_data) + "\r\n"

                # Send the JSON data to Client 2
                writer.write(data_to_send.encode('utf-8'))
                await writer.drain()  # Ensure the data is actually sent
                print(f"Sent JSON data to Client 2: {json_data}")

                # Optionally, wait for acknowledgment from Client 2
                try:
                    data = await reader.read(SOCKET_HEADER_SIZE)
                    if data:
                        recv_length = int(data.decode().strip())  # Read the length
                        acknowledgment = await reader.read(recv_length)  # Receive acknowledgment
                        print(f"Received from Client 2: {acknowledgment.decode()}")

                        # Send acknowledgment back to Flask server only
                        await send_acknowledgment_to_flask(acknowledgment.decode())
                    else:
                        print("No acknowledgment received from Client 2.")
                except asyncio.TimeoutError:
                    print("Timeout waiting for acknowledgment from Client 2.")
            else:
                print("No data fetched from Flask server to send to Client 2.")

            await asyncio.sleep(1)  # Delay before fetching new data again

    except asyncio.CancelledError:
        print("Client communication was canceled.")
    except Exception as e:
        print(f"Error while communicating with Client 2: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

# Function to send acknowledgment to Flask server
async def send_acknowledgment_to_flask(ack_data):
    try:
        async with aiohttp.ClientSession() as session:
            acknowledgment = {"acknowledgment": ack_data}

            # Send the acknowledgment to Flask server using POST
            async with session.post(FLASK_SERVER_URL, json=acknowledgment) as response:
                if response.status == 200:
                    print("Acknowledgment successfully sent to Flask server.")
                else:
                    print(f"Failed to send acknowledgment. Status code: {response.status}")
    except Exception as e:
        print(f"Error sending acknowledgment to Flask server: {e}")

# Function to start the server and accept connections from Client 2
async def start_server():
    server = await asyncio.start_server(handle_client, '0.0.0.0', SERVER_PORT)
    addr = server.sockets[0].getsockname()
    print(f'Server is running on {addr}')

    try:
        # Serve forever
        await server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped by user.")
    finally:
        # Gracefully close server
        server.close()
        await server.wait_closed()

# Start the server using asyncio
if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("Server stopped by user.")
