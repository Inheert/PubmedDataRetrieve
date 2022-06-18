from Pubmed import Pubmed
from PubmedGroup import PubmedGroup
Pubmed.default_pathologies["parathyroid diseases"] = "((hyperparathyroidism, primary) OR (primary hyperparathyroidism)) OR (hyperparathyroidism, secondary)"

test = PubmedGroup(pathologies=["parathyroid diseases"],
                   filters=["humans"], threadingObject=5, delay=0.5)
test.StartRetrieve()



