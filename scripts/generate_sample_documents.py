#!/usr/bin/env python3
"""
Generate sample PDFs for Finance, Medical, and News domains.
Output: data/documents/finance/, data/documents/medical/, data/documents/news/

Run from project root:
  python scripts/generate_sample_documents.py
"""
import sys
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fpdf import FPDF

from config import DATA_DIR

DOCS_DIR = DATA_DIR / "documents"


def _ascii_safe(s: str) -> str:
    """Replace common Unicode chars so default Helvetica (Latin-1) works."""
    return (
        s.replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )


def _add_section(pdf: FPDF, title: str, body: str, font_size_title: int = 14, font_size_body: int = 10):
    title = _ascii_safe(title)
    body = _ascii_safe(body)
    pdf.set_font("Helvetica", "B", font_size_title)
    pdf.multi_cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", font_size_body)
    pdf.multi_cell(0, 6, body, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)


def _write_pdf(path: Path, title: str, sections: list[tuple[str, str]]):
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 10, _ascii_safe(title), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    for sec_title, sec_body in sections:
        _add_section(pdf, sec_title, sec_body)
    pdf.output(path)
    print(f"  Wrote {path}")


# ---------- Finance: Income Tax Q&A ----------
FINANCE_INCOME_TAX = [
    ("What is the basic exemption limit for income tax in India (FY 2024-25)?",
     "For individuals below 60 years, the basic exemption limit is Rs 2.5 lakh. For senior citizens (60–80 years) it is Rs 3 lakh, and for super seniors (80+) it is Rs 5 lakh. Income up to these limits is not subject to tax."),
    ("What are the income tax slabs under the new regime?",
     "Under the new tax regime (optional): 0% up to Rs 3 lakh; 5% for Rs 3–7 lakh; 10% for Rs 7–10 lakh; 15% for Rs 10–12 lakh; 20% for Rs 12–15 lakh; 30% above Rs 15 lakh. Rebate under section 87A is available for total income up to Rs 7 lakh."),
    ("Is income from salary fully taxable?",
     "Income from salary is taxable under the head 'Salaries'. Basic salary, allowances (except those exempt like HRA, LTA as per rules), perquisites, and profit in lieu of salary are included. Standard deduction of Rs 75,000 is available to salaried individuals."),
    ("What is TDS on salary?",
     "TDS (Tax Deducted at Source) on salary is deducted by the employer based on the employee's estimated annual income and declared investments. The employer uses the applicable slab rates and deducts tax monthly. Form 16 is the TDS certificate issued by the employer."),
    ("Can I claim deduction for home loan interest?",
     "Yes. Under section 24(b), deduction for interest on home loan for a self-occupied property is allowed up to Rs 2 lakh per year. For let-out property, there is no such limit. Principal repayment is eligible for deduction under section 80C up to Rs 1.5 lakh."),
]

# ---------- Finance: GST Q&A ----------
FINANCE_GST = [
    ("What is GST and what are its types?",
     "GST (Goods and Services Tax) is an indirect tax levied on supply of goods and services. Types: CGST (Central) and SGST (State) for intra-state supply; IGST (Integrated) for inter-state supply. GST subsumed many earlier taxes like VAT, service tax, and excise."),
    ("What is the GST registration threshold?",
     "For normal category states, registration is required if aggregate turnover in a financial year exceeds Rs 40 lakh (goods) or Rs 20 lakh (services). For special category states it is Rs 20 lakh and Rs 10 lakh respectively. Voluntary registration is allowed."),
    ("What are the main GST rates?",
     "Common rates: 0% (essential items), 5% (e.g. edible oils, coal), 12% (e.g. processed food, medicines), 18% (e.g. soaps, capital goods), 28% (e.g. luxury items, sin goods). Some items are exempt."),
    ("How do I file GST returns?",
     "GSTR-1 (outward supplies) is filed monthly/quarterly. GSTR-3B (summary return with tax payment) is filed monthly. Annual return GSTR-9 is filed once a year. Filing is done on the GST portal (gov.in) before the due dates."),
    ("What is Input Tax Credit (ITC)?",
     "ITC allows you to claim credit for GST paid on inputs, input services, and capital goods used for business. You can set off ITC against output GST liability. ITC is not available for certain items like personal use, blocked credits under the law."),
]

# ---------- Medical: Diseases (cause, cure) ----------
MEDICAL_DISEASES = [
    ("Hypertension (High Blood Pressure)",
     "Cause: Often linked to lifestyle (high salt, low activity, stress), obesity, genetics, kidney or hormonal issues. Cure/Treatment: Lifestyle changes (diet, exercise, weight loss), reducing salt. Medicines include ACE inhibitors, beta-blockers, calcium channel blockers, diuretics. Regular monitoring and adherence to treatment are essential."),
    ("Type 2 Diabetes",
     "Cause: Insulin resistance and/or reduced insulin production; risk factors include obesity, sedentary lifestyle, family history, age. Cure/Treatment: Not fully curable but manageable. Diet control, regular exercise, oral hypoglycemics (e.g. metformin), or insulin. Blood sugar and HbA1c monitoring; foot and eye care."),
    ("Common Cold (Viral Upper Respiratory Infection)",
     "Cause: Viruses (e.g. rhinovirus). Spread by droplets and contact. Cure/Treatment: No specific cure; self-limiting in 7–10 days. Rest, fluids, paracetamol for fever/pain, decongestants or antihistamines for symptoms. Antibiotics are not indicated unless bacterial infection is confirmed."),
    ("Acute Gastritis",
     "Cause: Irritation of stomach lining by NSAIDs, alcohol, stress, H. pylori infection, or spicy food. Cure/Treatment: Avoid triggers; antacids, H2 blockers or proton-pump inhibitors (PPI). If H. pylori is present, antibiotic course. Small frequent meals and avoiding heavy/spicy food help."),
    ("Migraine",
     "Cause: Exact cause unclear; triggers include stress, sleep changes, certain foods, hormonal changes, bright lights. Cure/Treatment: No permanent cure. Acute: pain relievers, triptans. Preventive: identify triggers, beta-blockers or other prophylactic drugs. Rest in a dark, quiet room during attacks."),
]

# ---------- Medical: Sample prescriptions ----------
MEDICAL_PRESCRIPTIONS = [
    ("Sample prescription – Upper respiratory infection",
     "Patient: Adult. Diagnosis: Viral URTI. Rx: Paracetamol 500 mg 1–2 tablets 3 times daily after food for 3–5 days. Cetirizine 10 mg once at night for 5 days. Steam inhalation twice daily. Rest and adequate fluids. Review if fever persists beyond 3 days or breathing difficulty."),
    ("Sample prescription – Hypertension",
     "Patient: Adult. Diagnosis: Essential hypertension. Rx: Tab Amlodipine 5 mg once daily in the morning. Tab Telmisartan 40 mg once daily. Low salt diet, regular exercise, weight reduction if overweight. Check BP after 2 weeks and report. Avoid sudden stoppage of medicines."),
    ("Sample prescription – Type 2 Diabetes",
     "Patient: Adult. Diagnosis: Type 2 DM. Rx: Tab Metformin 500 mg with breakfast and dinner, increase to 1000 mg after 1 week if tolerated. Diet: low sugar, controlled carbs, small frequent meals. Daily walk 30 min. Fasting and PP blood sugar after 2 weeks; HbA1c after 3 months."),
    ("Sample prescription – Gastritis",
     "Patient: Adult. Diagnosis: Acute gastritis. Rx: Tab Pantoprazole 40 mg once in morning empty stomach for 2 weeks. Tab Domperidone 10 mg 3 times daily before meals for 5 days. Avoid NSAIDs, alcohol, spicy food. Small frequent meals. Review if pain or vomiting persists."),
]

# ---------- News: Sports ----------
NEWS_SPORTS = [
    ("Cricket: National team secures series win",
     "The national cricket team clinched the five-match series 3–1 with a dominant win in the fourth match. The captain praised the bowlers for restricting the opposition under 250. The final match will be played next week as a dead rubber; the team may rest key players."),
    ("Football: League title race goes to final day",
     "The top two sides won their penultimate matches, setting up a dramatic final weekend. Defending champions are one point ahead. A draw in the last game would be enough for them to retain the title. The challengers must win and hope for a slip-up."),
    ("Olympics: Two more athletes qualify",
     "Two athletes secured Olympic berths at the continental qualification event. One in track and field and one in swimming. The national Olympic committee confirmed the quotas. The total contingent for the Games now stands at 45 across 12 sports."),
]

# ---------- News: Politics ----------
NEWS_POLITICS = [
    ("Budget session concludes; key bills passed",
     "The budget session of Parliament concluded with the passage of the finance bill and three other key bills. The opposition staged walkouts during some debates. The government said the bills would boost growth and welfare. The next session is expected in July."),
    ("State elections: Polling in three phases",
     "Elections to the state assembly will be held in three phases next month. The election commission announced dates and model code of conduct is in force. Major parties have released manifestos focusing on jobs, agriculture, and infrastructure. Results will be declared in a single day after the last phase."),
    ("Cabinet reshuffle: Five new ministers sworn in",
     "Five new ministers were inducted into the cabinet in a reshuffle. Two portfolios were reallocated. The PM said the changes would strengthen governance and delivery. The opposition called it a diversion from current issues. The new ministers will assume charge from Monday."),
]

# ---------- News: Movies ----------
NEWS_MOVIES = [
    ("Blockbuster crosses 500 crore worldwide",
     "The recent release has crossed 500 crore in worldwide box office in two weeks. It is the fastest film this year to reach the mark. The lead actor thanked fans and the crew. The film is still running strongly in key markets. A sequel is under discussion."),
    ("Award-winning director announces new project",
     "The award-winning director announced their next project, a period drama set in the 1940s. The cast will be announced next month. Shooting is expected to start by year-end. The director said the script has been in the works for two years."),
    ("Streaming platform drops trailer of much-awaited series",
     "The streaming platform released the trailer of the much-awaited series. The show will have eight episodes and will drop in a single batch next month. The series is an adaptation of a popular novel. Fans have been reacting positively to the cast and the look of the show."),
]


def _finance_pdfs():
    base = DOCS_DIR / "finance"
    _write_pdf(
        base / "income_tax_qa.pdf",
        "Income Tax – Frequently Asked Questions",
        [(q, a) for q, a in FINANCE_INCOME_TAX],
    )
    _write_pdf(
        base / "gst_qa.pdf",
        "GST – Frequently Asked Questions",
        [(q, a) for q, a in FINANCE_GST],
    )


def _medical_pdfs():
    base = DOCS_DIR / "medical"
    _write_pdf(
        base / "common_diseases_cause_cure.pdf",
        "Common Diseases: Cause and Treatment",
        MEDICAL_DISEASES,
    )
    _write_pdf(
        base / "sample_prescriptions.pdf",
        "Sample Prescriptions (For Reference)",
        MEDICAL_PRESCRIPTIONS,
    )


def _news_pdfs():
    base = DOCS_DIR / "news"
    _write_pdf(
        base / "sports_news.pdf",
        "Sports News Digest",
        [(title, body) for title, body in NEWS_SPORTS],
    )
    _write_pdf(
        base / "politics_news.pdf",
        "Politics News Digest",
        [(title, body) for title, body in NEWS_POLITICS],
    )
    _write_pdf(
        base / "movie_news.pdf",
        "Movie & Entertainment News",
        [(title, body) for title, body in NEWS_MOVIES],
    )


def main():
    print("Generating sample PDFs in", DOCS_DIR)
    print("\nFinance:")
    _finance_pdfs()
    print("\nMedical:")
    _medical_pdfs()
    print("\nNews:")
    _news_pdfs()
    print("\nDone. Ingest with:")
    print("  python -m ingestion.ingest_pdfs --domain finance --path", DOCS_DIR / "finance")
    print("  python -m ingestion.ingest_pdfs --domain medical --path", DOCS_DIR / "medical")
    print("  python -m ingestion.ingest_pdfs --domain news --path", DOCS_DIR / "news")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
