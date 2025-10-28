def handler(request, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': '{"status": "ok", "message": "Application is running"}'
    }