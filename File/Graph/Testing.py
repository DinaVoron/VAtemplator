"""
pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download ru_core_news_sm

pip install networkx
pip install pyvis
"""



semantic_network = {
    "nodes": [
        {
            "id": 1,
            "node": {
                "text": ["2000"],
                "pos": ["NUM"],
                "type": 2
            },
            "layer": [1, 2, 5, 76]
        },

        '...'
    ],
    "edges": [
        {
            "id-f": 1,
            "id-t": 2,
            "edge": {
                "text": "amod",
                "type": 0
            },
            "layer": [1, 2]
        },

        '...'
    ]
}