from Pubmed import Pubmed
from PubmedGroup import PubmedGroup

# Pubmed.default_pathologies["parathyroid diseases"] = "((hyperparathyroidism, primary) OR (primary hyperparathyroidism)) OR (hyperparathyroidism, secondary)"

test = PubmedGroup(pathologies=[x for x in Pubmed.default_pathologies.keys()],
                   filters=["humans"], threadingObject=5, delay=0.8)
test.StartRetrieve()
test.JoinAndCleanDataframe()
