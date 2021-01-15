all: plone/app/standardtiles/embed_providers.py

plone/app/standardtiles/embed_providers.py: generate_embed_providers.py
	./generate_embed_providers.py > plone/app/standardtiles/embed_providers.py

