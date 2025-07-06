import os
import tempfile
import gradio as gr
import pandas as pd

def find_unverified(hbl_file, tre_file):
    try:
        hbl_df = pd.read_excel(hbl_file.name if hasattr(hbl_file, "name") else hbl_file)
        tre_df = pd.read_excel(tre_file.name if hasattr(tre_file, "name") else tre_file)

        merged = pd.merge(
            hbl_df,
            tre_df,
            on=["StudentID", "Name", "Program", "Semester"],
            how="left",
            suffixes=("_HBL", "_TRE"),
        )

        mask = merged["Verified_HBL"].astype(str).str.lower().isin({"no", "false", "0"})
        unverified_df = merged[mask]

        if unverified_df.empty:
            return pd.DataFrame(), "✅ All students are verified!", None

        tmpdir = tempfile.mkdtemp()
        out_path = os.path.join(tmpdir, "unverified_students.xlsx")
        unverified_df.to_excel(out_path, index=False)

        return unverified_df, f"🔎 Found {len(unverified_df)} unverified students.", out_path

    except Exception as e:
        return pd.DataFrame(), f"❌ Error: {e}", None

with gr.Blocks(title="Student Fee Verification") as demo:
    gr.Markdown("## 📋 Student Fee Unverified Checker")

    with gr.Row():
        hbl_file = gr.File(label="📤 Upload HBL Bank Sheet (.xlsx)")
        tre_file = gr.File(label="📤 Upload Treasurer Office Sheet (.xlsx)")

    submit_btn   = gr.Button("🔍 Find Unverified Students")
    result_table = gr.Dataframe(label="Unverified Students")
    status_box   = gr.Textbox(label="Status / Errors")
    download_btn = gr.File(label="⬇️ Download Result (.xlsx)")

    submit_btn.click(
        fn=find_unverified,
        inputs=[hbl_file, tre_file],
        outputs=[result_table, status_box, download_btn],
    )

    gr.HTML("""
    <div style='display:flex;justify-content:space-between;margin-top:30px'>
        <span style='font-size:14px;color:#777'>
            © Powered by <strong>Dr. Adeel Anjum – Statistical Data Scientist</strong>
        </span>
        <a href='/logout' target='_self'>
            <button style='background:#d9534f;color:white;padding:10px 15px;
                           font-size:16px;border:none;border-radius:5px'>
                🔒 Logout
            </button>
        </a>
    </div>
    """)

if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=8080)
