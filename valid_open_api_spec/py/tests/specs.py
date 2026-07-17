valid = {
    "openapi": "3.0.0",
    "info": {"title": "API", "version": "1.0.0"},
    "paths": {
        "/people": {
            "get": {
                "summary": "Get all people",
                "responses": {"200": {"description": "OK"}},
            },
            "post": {
                "summary": "Create a new person",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Person"}
                        }
                    },
                },
                "responses": {"201": {"description": "Created"}},
            },
        },
        "/people/{personId}": {
            "get": {
                "summary": "Get a person by ID",
                "parameters": [
                    {
                        "name": "personId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {"200": {"description": "OK"}},
            },
            "put": {
                "summary": "Update a person by ID",
                "parameters": [
                    {
                        "name": "personId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Person"}
                        }
                    },
                },
                "responses": {"200": {"description": "OK"}},
            },
            "delete": {
                "summary": "Delete a person by ID",
                "parameters": [
                    {
                        "name": "personId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {"204": {"description": "No Content"}},
            },
        },
        "/properties": {
            "get": {
                "summary": "Get all properties",
                "responses": {"200": {"description": "OK"}},
            },
            "post": {
                "summary": "Create a new property",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Property"}
                        }
                    },
                },
                "responses": {"201": {"description": "Created"}},
            },
        },
        "/properties/{propertyId}": {
            "get": {
                "summary": "Get a property by ID",
                "parameters": [
                    {
                        "name": "propertyId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {"200": {"description": "OK"}},
            },
            "put": {
                "summary": "Update a property by ID",
                "parameters": [
                    {
                        "name": "propertyId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Property"}
                        }
                    },
                },
                "responses": {"200": {"description": "OK"}},
            },
            "delete": {
                "summary": "Delete a property by ID",
                "parameters": [
                    {
                        "name": "propertyId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {"204": {"description": "No Content"}},
            },
        },
    },
    "components": {
        "schemas": {
            "Person": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "firstName": {"type": "string"},
                    "lastName": {"type": "string"},
                    "age": {"type": "integer"},
                    "familyMembers": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/Person"},
                    },
                    "property": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/Property"},
                    },
                },
                "required": ["id", "firstName", "lastName", "age"],
                "additionalProperties": False,
            },
            "Property": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "type": {"type": "string"},
                    "price": {"type": "number"},
                    "owner": {"type": "string"},
                },
                "required": ["id", "type", "price", "owner"],
                "additionalProperties": False,
            },
        }
    },
}

invalid = {
    "openapi": "3.0.0",
    "info": {
        "title": "API",
    },
    "paths": {
        "/people": {
            "get": {
                "summary": "Get all people",
                "responses": {"200": {"description": "OK"}},
            },
            "post": {
                "summary": "Create a new person",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Person"}
                        }
                    },
                },
                "responses": {"201": {"description": "Created"}},
            },
        },
        "/people/{personId}": {
            "get": {
                "summary": "Get a person by ID",
                "parameters": [
                    {
                        "name": "personId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {"200": {"description": "OK"}},
            },
            "put": {
                "summary": "Update a person by ID",
                "parameters": [
                    {
                        "name": "personId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Person"}
                        }
                    },
                },
                "responses": {"200": {"description": "OK"}},
            },
            "delete": {
                "summary": "Delete a person by ID",
                "parameters": [
                    {
                        "name": "personId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {"204": {"description": "No Content"}},
            },
        },
        "/properties": {
            "get": {
                "summary": "Get all properties",
                "responses": {"200": {"description": "OK"}},
            },
            "post": {
                "summary": "Create a new property",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Property"}
                        }
                    },
                },
                "responses": {"201": {"description": "Created"}},
            },
        },
        "/properties/{propertyId}": {
            "get": {
                "summary": "Get a property by ID",
                "parameters": [
                    {
                        "name": "propertyId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {"200": {"description": "OK"}},
            },
            "put": {
                "summary": "Update a property by ID",
                "parameters": [
                    {
                        "name": "propertyId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Property"}
                        }
                    },
                },
                "responses": {"200": {"description": "OK"}},
            },
            "delete": {
                "summary": "Delete a property by ID",
                "parameters": [
                    {
                        "name": "propertyId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {"204": {"description": "No Content"}},
            },
        },
    },
    "components": {
        "schemas": {
            "Person": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "firstName": {"type": "string"},
                    "lastName": {"type": "string"},
                    "age": {"type": "integer"},
                    "familyMembers": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/Person"},
                    },
                    "property": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/Property"},
                    },
                },
                "required": ["id", "firstName", "lastName", "age"],
                "additionalProperties": False,
            },
            "Property": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "type": {"type": "string"},
                    "price": {"type": "number"},
                    "owner": {"type": "string"},
                },
                "required": ["id", "type", "price", "owner"],
                "additionalProperties": False,
            },
        }
    },
}
