
from ibm_watsonx_ai.foundation_models import ModelInference 
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams



project_id = "a15722af-476f-4ad2-ad25-090750dd14e2"
url = "https://us-south.ml.cloud.ibm.com"
apikey = "Nt8BVcy9pRD8bDngmalyAujN02hPV7PsuJu6bpUr6zxN"


credentials = {
    "apikey": apikey,
    "url": url
}
watsonx_model = ModelInference(
    model_id="ibm/granite-13b-instruct-v2",
    credentials=credentials,
    project_id=project_id
)

def generate(prompt, max_tokens=500):
    params = {
        GenParams.DECODING_METHOD: "greedy",
        GenParams.MAX_NEW_TOKENS: max_tokens,
        GenParams.TEMPERATURE: 0.2
    }
    response = watsonx_model.generate_text(
        prompt=prompt,
        params=params,
        guardrails=False,
    )
    #return response['results'][0]['generated_text']
    return response