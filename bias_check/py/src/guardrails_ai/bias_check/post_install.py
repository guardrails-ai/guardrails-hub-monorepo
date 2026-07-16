from transformers.pipelines import pipeline

print("post-install starting...")
_ = pipeline(
    "text-classification",
    model="d4data/bias-detection-model",
    tokenizer="d4data/bias-detection-model",
    framework="tf",
    torch_dtype=None,  # For transformers <4.56
    dtype=None,  # For transformers >4.56
)
print("post-install complete!")
