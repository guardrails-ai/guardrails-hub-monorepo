from fastapi import HTTPException  # type: ignore
from pydantic import BaseModel
from typing import List, Tuple
import torch
import os
from models_host.base_inference_spec import BaseInferenceSpec  # type: ignore

from transformers import pipeline


class InferenceData(BaseModel):
    name: str
    shape: List[int]
    data: List
    datatype: str


class InputRequest(BaseModel):
    inputs: List[InferenceData]


class OutputResponse(BaseModel):
    modelname: str
    modelversion: str
    outputs: List[InferenceData]


class InferenceSpec(BaseInferenceSpec):
    model_name = "michellejieli/NSFW_text_classifier"

    @property
    def torch_device(self):
        env = os.environ.get("env", "dev")
        torch_device = "cuda" if env == "prod" else "cpu"
        return torch_device

    def load(self):
        model_name = self.model_name
        torch_device = self.torch_device
        print(f"Loading model {model_name} using device {torch_device}...")
        self.model = pipeline(
            "text-classification", model=model_name, device=torch.device(torch_device)
        )

    def process_request(self, input_request: InputRequest) -> Tuple[Tuple, dict]:
        text_vals = None
        threshold = None
        for inp in input_request.inputs:
            if inp.name == "text":
                text_vals = inp.data
            elif inp.name == "threshold":
                threshold = float(inp.data[0])

        if text_vals is None or threshold is None:
            raise HTTPException(status_code=400, detail="Invalid input format")

        args = (text_vals, threshold)
        kwargs = {}
        return args, kwargs

    def infer(self, text_vals, threshold) -> OutputResponse:
        outputs = []
        for idx, text in enumerate(text_vals):
            results = self.model(text)
            pred_labels = [
                result["label"]
                for result in results
                if result["label"] == "NSFW" and result["score"] > threshold
            ]
            outputs.append(
                InferenceData(
                    name=f"result{idx}",
                    datatype="BYTES",
                    shape=[len(pred_labels)],
                    data=[pred_labels],
                )
            )

        output_data = OutputResponse(
            modelname=self.model_name, modelversion="1", outputs=outputs
        )

        return output_data
