from django.db import models


class LNPFormulation(models.Model):
    """4-component LNP formulation with molar ratios.
    Central entity connecting lipids to experiments.
    """

    class MixingMethod(models.TextChoices):
        MICROFLUIDICS = "microfluidics", "Microfluidics"
        HANDMIXED = "handmixed", "Hand Mixed"

    class Source(models.TextChoices):
        LNPDB = "lnpdb", "LNPDB"
        DESIGNED = "designed", "AI Designed"
        MANUAL = "manual", "Manual"

    formulation_id = models.CharField(max_length=100, unique=True, db_index=True)

    # 4 core components + molar ratios
    ionizable_lipid = models.ForeignKey(
        "compounds.IonizableLipid", on_delete=models.CASCADE, related_name="formulations"
    )
    il_molratio = models.FloatField(help_text="Ionizable lipid molar ratio")

    helper_lipid = models.ForeignKey(
        "compounds.HelperLipid", on_delete=models.SET_NULL, null=True, blank=True, related_name="formulations"
    )
    hl_molratio = models.FloatField(null=True, blank=True)

    cholesterol = models.ForeignKey(
        "compounds.Cholesterol", on_delete=models.SET_NULL, null=True, blank=True, related_name="formulations"
    )
    chl_molratio = models.FloatField(null=True, blank=True)

    peg_lipid = models.ForeignKey(
        "compounds.PEGLipid", on_delete=models.SET_NULL, null=True, blank=True, related_name="formulations"
    )
    peg_molratio = models.FloatField(null=True, blank=True)

    # Optional 5th component
    fifth_component_name = models.CharField(max_length=200, blank=True, default="")
    fifth_component_smiles = models.TextField(blank=True, default="")
    fifth_component_molratio = models.FloatField(null=True, blank=True)

    # Preparation parameters
    il_to_na_massratio = models.FloatField(null=True, blank=True, help_text="IL:nucleic acid mass ratio")
    il_to_na_chargeratio = models.FloatField(null=True, blank=True, help_text="IL:nucleic acid charge ratio (N/P)")
    mixing_method = models.CharField(max_length=20, choices=MixingMethod.choices, default=MixingMethod.MICROFLUIDICS)
    aqueous_buffer = models.CharField(max_length=200, blank=True, default="")
    dialysis_buffer = models.CharField(max_length=200, blank=True, default="")

    source = models.CharField(max_length=20, choices=Source.choices, default=Source.LNPDB)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.formulation_id

    @property
    def composition_str(self):
        """Human-readable composition like 'IL:HL:Chol:PEG = 50:10:38.5:1.5'"""
        parts = [f"{self.il_molratio}"]
        if self.hl_molratio: parts.append(f"{self.hl_molratio}")
        if self.chl_molratio: parts.append(f"{self.chl_molratio}")
        if self.peg_molratio: parts.append(f"{self.peg_molratio}")
        return ":".join(parts)
