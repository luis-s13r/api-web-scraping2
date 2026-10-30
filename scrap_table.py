import requests
import boto3
import uuid

def lambda_handler(event, context):
    # URL que devuelve los datos de la tabla en JSON
    url = "https://ultimosismo.igp.gob.pe/api/ultimo-sismo/ajaxb/2026"

    # Realizar la solicitud HTTP
    response = requests.get(url)
    if response.status_code != 200:
        return {
            'statusCode': response.status_code,
            'body': 'Error al acceder a la página web'
        }

    # Obtener los 10 reportes más recientes directamente del JSON
    rows = sorted(
        response.json(),
        key=lambda sismo: sismo['codigo'],
        reverse=True
    )[:10]

    # Guardar los datos en DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('TablaWebScrapping2')

    # Eliminar los elementos encontrados por el scan
    scan = table.scan()
    with table.batch_writer() as batch:
        for each in scan['Items']:
            batch.delete_item(
                Key={
                    'id': each['id']
                }
            )

    # Insertar los nuevos datos
    i = 1
    for row in rows:
        row['#'] = i
        row['id'] = str(uuid.uuid4())
        table.put_item(Item=row)
        i = i + 1

    # Retornar el resultado
    return {
        'statusCode': 200,
        'body': rows
    }