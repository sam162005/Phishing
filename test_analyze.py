import requests

# Test the analyze feature
url = "http://127.0.0.1:5000/analyze"

# Test with fake review example
fake_review = "love this product great quality best buy ever"
data = {"review_text": fake_review}
response = requests.post(url, data=data)

if response.status_code == 200:
    print("✅ Analyze feature is working!")
    print("Response HTML contains result:", "result" in response.text)
    print("Fake review test passed.")
else:
    print("❌ Analyze feature failed with status code:", response.status_code)

# Test with real review example
real_review = "I bought this for my kitchen and it works perfectly. The material feels sturdy and the design is simple but effective. It arrived on time and was well-packaged."
data = {"review_text": real_review}
response = requests.post(url, data=data)

if response.status_code == 200:
    print("Real review test passed.")
else:
    print("❌ Real review test failed with status code:", response.status_code)
