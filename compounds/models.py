from django.db import models


class HeadGroup(models.Model):
    """Ionizable lipid head group (amine-containing)."""
    name = models.CharField(max_length=200, unique=True)
    smiles = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Linker(models.Model):
    """Linker connecting head to tails."""

    class LinkerType(models.TextChoices):
        ESTER = "ester", "Ester"
        CARBONATE = "carbonate", "Carbonate"
        DISULFIDE = "disulfide", "Disulfide"
        AMIDE = "amide", "Amide"
        ETHER = "ether", "Ether"
        OTHER = "other", "Other"

    name = models.CharField(max_length=200, unique=True)
    smiles = models.TextField(blank=True, default="")
    linker_type = models.CharField(max_length=20, choices=LinkerType.choices, default=LinkerType.OTHER)

    def __str__(self):
        return self.name


class Tail(models.Model):
    """Hydrophobic tail chain."""
    name = models.CharField(max_length=200, unique=True)
    smiles = models.TextField(blank=True, default="")
    carbon_count = models.IntegerField(null=True, blank=True)
    is_branched = models.BooleanField(default=False)
    has_unsaturation = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class IonizableLipid(models.Model):
    """Core entity: ionizable lipid with molecular descriptors.
    Maps to IL_* columns in LNPDB. 13,028 unique structures.
    """

    class Source(models.TextChoices):
        LNPDB = "lnpdb", "LNPDB"
        LITERATURE = "literature", "Literature"
        GENERATED = "generated", "AI Generated"
        SYNTHESIZED = "synthesized", "Synthesized"

    # Identity
    name = models.CharField(max_length=300, db_index=True)
    smiles = models.TextField(db_index=True)
    protonated_smiles = models.TextField(blank=True, default="")

    # Structural components (nullable - not all lipids decomposed)
    head_group = models.ForeignKey(HeadGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name="lipids")
    linker = models.ForeignKey(Linker, on_delete=models.SET_NULL, null=True, blank=True, related_name="lipids")
    tail1 = models.ForeignKey(Tail, on_delete=models.SET_NULL, null=True, blank=True, related_name="lipids_tail1")
    tail2 = models.ForeignKey(Tail, on_delete=models.SET_NULL, null=True, blank=True, related_name="lipids_tail2")
    tail3 = models.ForeignKey(Tail, on_delete=models.SET_NULL, null=True, blank=True, related_name="lipids_tail3")
    tail4 = models.ForeignKey(Tail, on_delete=models.SET_NULL, null=True, blank=True, related_name="lipids_tail4")

    # 17 Molecular Descriptors (from LNPDB or RDKit-calculated)
    molecular_weight = models.FloatField(null=True, blank=True, db_index=True)
    logp = models.FloatField(null=True, blank=True, db_index=True)
    tpsa = models.FloatField(null=True, blank=True, help_text="Topological Polar Surface Area")
    heavy_atoms = models.IntegerField(null=True, blank=True)
    rings = models.IntegerField(null=True, blank=True)
    aromatic_rings = models.IntegerField(null=True, blank=True)
    rotatable_bonds = models.IntegerField(null=True, blank=True)
    vdw_volume = models.FloatField(null=True, blank=True, help_text="van der Waals Volume")
    hbd = models.IntegerField(null=True, blank=True, help_text="H-Bond Donors")
    hba = models.IntegerField(null=True, blank=True, help_text="H-Bond Acceptors")
    molar_refractivity = models.FloatField(null=True, blank=True)
    fsp3 = models.FloatField(null=True, blank=True, help_text="Fraction sp3 Carbons")
    sp3_carbons = models.IntegerField(null=True, blank=True)
    nitrogen_count = models.IntegerField(null=True, blank=True)

    # Structural flags (biodegradable linker types)
    has_ester = models.BooleanField(default=False)
    has_carbonate = models.BooleanField(default=False)
    has_disulfide = models.BooleanField(default=False)

    # Metadata
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.LNPDB)
    publication_link = models.URLField(blank=True, default="")
    publication_pmid = models.CharField(max_length=20, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["molecular_weight", "logp"]),
            models.Index(fields=["has_ester", "has_carbonate", "has_disulfide"]),
        ]

    def __str__(self):
        return f"{self.name} (MW={self.molecular_weight})"

    @property
    def descriptor_dict(self):
        """Return all descriptors as dict for AI model input."""
        return {
            "molecular_weight": self.molecular_weight,
            "logp": self.logp,
            "tpsa": self.tpsa,
            "heavy_atoms": self.heavy_atoms,
            "rings": self.rings,
            "aromatic_rings": self.aromatic_rings,
            "rotatable_bonds": self.rotatable_bonds,
            "vdw_volume": self.vdw_volume,
            "hbd": self.hbd,
            "hba": self.hba,
            "molar_refractivity": self.molar_refractivity,
            "fsp3": self.fsp3,
            "sp3_carbons": self.sp3_carbons,
            "nitrogen_count": self.nitrogen_count,
        }


class HelperLipid(models.Model):
    """Helper lipid component (DOPE, DSPC, etc). 7 types in LNPDB."""
    name = models.CharField(max_length=200, unique=True)
    smiles = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name


class Cholesterol(models.Model):
    """Cholesterol variants. 16 types in LNPDB."""
    name = models.CharField(max_length=200, unique=True)
    smiles = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name


class PEGLipid(models.Model):
    """PEG-lipid component (DMG-PEG2000, etc). 15 types in LNPDB."""
    name = models.CharField(max_length=200, unique=True)
    smiles = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name
