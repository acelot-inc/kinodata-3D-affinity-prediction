from typing import Tuple

from torch import Tensor
from torch.nn import Module, ModuleList, Sequential, Linear, Embedding
from torch_geometric.nn import GINEConv, LayerNorm

from kinodata.types import NodeType, RelationType
from kinodata.data.featurization.bonds import NUM_BOND_TYPES
from kinodata.data.featurization.atoms import AtomFeatures

from kinodata.model.shared.node_embedding import (
    CombineSum,
    AtomTypeEmbedding,
    FeatureEmbedding,
)
from kinodata.model.resolve import resolve_act


class GINE(Module):
    def __init__(
        self, channels: int, num_layers: int, edge_channels: int, act: str = "silu"
    ) -> None:
        super().__init__()
        self.act = resolve_act(act)
        self.conv_layers = ModuleList()
        self.norm_layers = ModuleList()
        for _ in range(num_layers):
            nn = Sequential(
                Linear(channels, channels), self.act, Linear(channels, channels)
            )
            self.conv_layers.append(GINEConv(nn, edge_dim=channels))
            self.norm_layers.append(LayerNorm(channels))
        self.lin_edge = Sequential(Linear(edge_channels, channels), self.act)

    def forward(self, x: Tensor, edge_index: Tensor, edge_attr: Tensor) -> Tensor:
        edge_attr = self.lin_edge(edge_attr.float())
        for conv, norm in zip(self.conv_layers, self.norm_layers):
            x = norm(x + conv(x=x, edge_index=edge_index, edge_attr=edge_attr))
        return x


class LigandGINE(Module):
    def __init__(self, hidden_channels: int, num_layers: int, act: str) -> None:
        super().__init__()
        self.initial_embedding = CombineSum(
            [
                AtomTypeEmbedding(
                    NodeType.Ligand,
                    hidden_chanels=hidden_channels,
                ),
                FeatureEmbedding(
                    NodeType.Ligand,
                    in_channels=AtomFeatures.size,
                    hidden_channels=hidden_channels,
                    act=act,
                ),
            ]
        )
        self.gine = GINE(
            hidden_channels, num_layers, edge_channels=NUM_BOND_TYPES, act=act
        )

    def forward(self, batch) -> Tuple[Tensor, Tensor]:
        ligand_node_store = batch[NodeType.Ligand]
        ligand_bond_store = batch[
            NodeType.Ligand, RelationType.Covalent, NodeType.Ligand
        ]
        x = self.initial_embedding(batch)
        h = self.gine(
            x=x,
            edge_index=ligand_bond_store.edge_index,
            edge_attr=ligand_bond_store.edge_attr,
        )
        return h, ligand_node_store.batch
