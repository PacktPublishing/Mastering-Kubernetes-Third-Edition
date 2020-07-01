def yeah(event, context):
  print(event)
  print(context)
  return b'Yeah, ' + event['data']