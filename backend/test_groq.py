import os, asyncio
from groq import AsyncGroq
client = AsyncGroq(api_key=os.environ.get('GROQ_API_KEY', ''))
async def test():
    try:
        res = await client.chat.completions.create(messages=[{'role':'user','content':'hi'}], model='llama-3.3-70b-versatile', max_tokens=10)
        print(res)
    except Exception as e:
        print('Error:', type(e), e)
asyncio.run(test())
