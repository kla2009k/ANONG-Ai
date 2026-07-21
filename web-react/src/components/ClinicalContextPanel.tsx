import { ClipboardPlus } from "lucide-react";
import type { ClinicalContext } from "@/lib/api";

export const SYMPTOM_OPTIONS = [
  ["intermenstrual_bleeding", "Bleeding between periods"],
  ["postcoital_bleeding", "Bleeding after sex"],
  ["postmenopausal_bleeding", "Bleeding after menopause"],
  ["unusual_discharge", "Unusual or foul-smelling discharge"],
  ["persistent_pelvic_back_leg_pain", "Persistent pelvic, back, or leg pain"],
  ["weight_loss_fatigue_appetite_loss", "Unexplained weight loss, fatigue, or appetite loss"],
] as const;

export const SYMPTOM_LABELS = Object.fromEntries(SYMPTOM_OPTIONS) as Record<string, string>;

export const EMPTY_CLINICAL_CONTEXT: ClinicalContext = {
  age_years: null,
  symptoms: [],
  other_symptoms: "",
  specimen_type: "unknown",
  last_screening: "unknown",
  hpv_test: "not_performed",
  hpv_genotype: "",
  prior_abnormal_result: false,
  immunocompromised: false,
  pregnant: false,
};

export function ClinicalContextPanel({ value, onChange }: {
  value: ClinicalContext;
  onChange: (value: ClinicalContext) => void;
}) {
  const update = <K extends keyof ClinicalContext>(key: K, next: ClinicalContext[K]) => onChange({ ...value, [key]: next });
  const toggleSymptom = (key: string) => update(
    "symptoms",
    value.symptoms.includes(key) ? value.symptoms.filter((item) => item !== key) : [...value.symptoms, key],
  );

  return (
    <section className="mt-6 rounded-lg border border-line bg-surface p-5" aria-labelledby="clinical-context-title">
      <div className="flex items-start gap-3">
        <ClipboardPlus className="mt-0.5 shrink-0 text-teal" size={20} aria-hidden />
        <div>
          <h2 id="clinical-context-title" className="font-display text-lg font-semibold text-ink">Optional clinical context</h2>
          <p className="mt-1 text-xs leading-5 text-mut">Used only for report safety and clinician review. These fields never change the image model prediction. Do not enter a name, national ID, phone number, or other direct identifier.</p>
        </div>
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-3">
        <label className="text-xs text-mut">Age in years
          <input type="number" min={10} max={120} value={value.age_years ?? ""}
            onChange={(event) => update("age_years", event.target.value ? Number(event.target.value) : null)}
            className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm text-ink" placeholder="Not entered" />
        </label>
        <label className="text-xs text-mut">Specimen type
          <select value={value.specimen_type} onChange={(event) => update("specimen_type", event.target.value as ClinicalContext["specimen_type"])} className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm text-ink">
            <option value="unknown">Unknown / not entered</option><option value="thinprep_lbc">ThinPrep / liquid-based cytology</option><option value="conventional_pap">Conventional Pap smear</option>
          </select>
        </label>
        <label className="text-xs text-mut">Last cervical screening
          <select value={value.last_screening} onChange={(event) => update("last_screening", event.target.value as ClinicalContext["last_screening"])} className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm text-ink">
            <option value="unknown">Unknown</option><option value="never">Never screened</option><option value="within_3_years">Within 3 years</option><option value="3_to_5_years">3-5 years ago</option><option value="over_5_years">Over 5 years ago</option>
          </select>
        </label>
      </div>

      <fieldset className="mt-4">
        <legend className="text-xs font-semibold text-ink">Reported symptoms</legend>
        <p className="mt-1 text-[11px] text-mut">Any reported symptom requires separate clinical evaluation; a NILM AI result must not be used for reassurance.</p>
        <div className="mt-2 grid gap-x-5 gap-y-2 md:grid-cols-2">
          {SYMPTOM_OPTIONS.map(([key, label]) => (
            <label key={key} className="flex items-start gap-2 text-xs leading-5 text-mut">
              <input type="checkbox" checked={value.symptoms.includes(key)} onChange={() => toggleSymptom(key)} className="mt-1 accent-[var(--teal)]" />
              <span>{label}</span>
            </label>
          ))}
        </div>
        <label className="mt-3 block text-xs text-mut">Other reported symptoms
          <textarea value={value.other_symptoms} maxLength={500} onChange={(event) => update("other_symptoms", event.target.value)} rows={2} className="mt-1 w-full resize-y rounded-lg border border-line bg-paper px-3 py-2 text-sm text-ink" placeholder="Optional; avoid direct identifiers" />
        </label>
      </fieldset>

      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <label className="text-xs text-mut">Separate laboratory HPV test
          <select value={value.hpv_test} onChange={(event) => update("hpv_test", event.target.value as ClinicalContext["hpv_test"])} className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm text-ink">
            <option value="not_performed">Not performed</option><option value="unknown">Unknown</option><option value="negative">Negative</option><option value="positive">Positive</option>
          </select>
        </label>
        <label className="text-xs text-mut">HPV genotype from laboratory report
          <input value={value.hpv_genotype} disabled={value.hpv_test !== "positive"} maxLength={80} onChange={(event) => update("hpv_genotype", event.target.value)} className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm text-ink disabled:opacity-50" placeholder="For example, 16 or 18; do not infer from image" />
        </label>
      </div>
      <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2">
        {([ ["prior_abnormal_result", "Prior abnormal screening result"], ["immunocompromised", "Immunocompromised"], ["pregnant", "Pregnant"] ] as const).map(([key, label]) => (
          <label key={key} className="flex items-center gap-2 text-xs text-mut"><input type="checkbox" checked={value[key]} onChange={(event) => update(key, event.target.checked)} className="accent-[var(--teal)]" />{label}</label>
        ))}
      </div>
    </section>
  );
}
