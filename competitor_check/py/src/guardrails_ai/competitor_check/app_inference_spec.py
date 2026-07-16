from fastapi import HTTPException  # type: ignore
from pydantic import BaseModel
from typing import List, Tuple
import spacy
import logging
from models_host.base_inference_spec import BaseInferenceSpec  # type: ignore

logger = logging.getLogger("competitor-check")

try:
    spacy.require_gpu()  # type: ignore
except Exception as e:
    logger.warning(f"Failed to enable GPU, falling back to CPU: {e}")


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
    model_name = "en_core_web_trf"
    model = None

    def load(self):
        model_name = self.model_name
        print(f"Loading model {model_name}...")
        if not spacy.util.is_package(model_name):
            print(
                f"Spacy model {model_name} not installed. "
                "Download should start now and take a few minutes."
            )
            spacy.cli.download(model_name)  # type: ignore
        self.model = spacy.load(model_name)

    def process_request(self, input_request: InputRequest) -> Tuple[Tuple, dict]:
        text_vals = None
        competitors = []
        for inp in input_request.inputs:
            if inp.name == "text":
                text_vals = inp.data
            elif inp.name == "competitors":
                competitors = inp.data

        if text_vals is None or competitors is None:
            raise HTTPException(status_code=400, detail="Invalid input format")

        args = (text_vals, competitors)
        kwargs = {}
        return args, kwargs

    def infer(self, text_vals, competitors) -> OutputResponse:
        outputs = []
        for idx, text in enumerate(text_vals):
            doc = self.model(text)  # type: ignore

            located_competitors = []
            for ent in doc.ents:
                if ent.text in competitors:
                    located_competitors.append(ent.text)

            outputs.append(
                InferenceData(
                    name=f"result{idx}",
                    datatype="BYTES",
                    shape=[1],
                    data=[located_competitors],
                )
            )

        output_data = OutputResponse(
            modelname=self.model_name, modelversion="1", outputs=outputs
        )

        return output_data
