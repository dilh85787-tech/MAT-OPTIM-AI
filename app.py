import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(page_title="MAT-OPTIM AI", page_icon="⚙️", layout="wide")

DATA_DIR = Path(__file__).parent / "data"
DB_PATH = DATA_DIR / "materials.csv"

st.markdown("""
<style>
.main {direction: rtl;}
[data-testid="stSidebar"] {direction: rtl;}
h1,h2,h3 {text-align: right;}
div[data-testid="stMarkdownContainer"] p {text-align: right;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_materials():
    return pd.read_csv(DB_PATH)

materials = load_materials()

st.title("⚙️ MAT-OPTIM AI")
st.subheader("مساعد ذكي لاختيار المواد الهندسية واستبدالها وتحسين المكونات الميكانيكية")
st.caption("نسخة أولية MVP — البيانات التوضيحية لا تُستخدم لاعتماد تصميم صناعي أو قرار سلامة.")

with st.sidebar:
    st.header("إعدادات الاستخدام")
    mode = st.radio("اختر طريقة الاستخدام", ["المستخدم غير المتخصص — Mode Simple", "المهندس والتقني — Mode Expert"])
    st.divider()
    st.markdown("**MAT-OPTIM AI**")
    st.caption("Prototype académique | Génie mécanique & génie des matériaux")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "حل مشكلة واختيار مادة", "قاعدة المواد", "المواد البديلة", "حساب ميكانيكي أولي", "التنبؤ بعمر التعب"
])

# Helpers
def safe_num(x):
    try:
        return float(x)
    except Exception:
        return np.nan

with tab1:
    st.header("وصف المشكلة والحصول على توصية")
    if mode.startswith("المستخدم غير"):
        st.write("صف المشكلة بلغتك العادية. ستُحوّل الإجابات إلى خصائص مطلوبة بصورة أولية.")
        problem = st.text_area("ما المشكلة التي تواجهها؟", placeholder="مثال: القطعة ثقيلة وتتآكل في وسط رطب وأريد بديلاً أقل تكلفة.")
        c1, c2 = st.columns(2)
        with c1:
            application = st.selectbox("مجال الاستخدام", ["قطعة ميكانيكية عامة", "السيارات", "معدات صناعية", "هياكل خفيفة", "أجزاء معرضة للاحتكاك", "استخدام آخر"])
            environment = st.selectbox("ظروف الوسط", ["عادي / داخلي", "رطوبة أو ماء", "حرارة مرتفعة", "احتكاك أو تآكل سطحي", "وسط كيميائي"])
        with c2:
            priority = st.selectbox("ما الأولوية الأهم؟", ["توازن بين الخصائص", "تقليل الوزن", "مقاومة ميكانيكية", "مقاومة التآكل", "خفض التكلفة"])
            budget = st.selectbox("مستوى الميزانية", ["منخفضة", "متوسطة", "مرتفعة", "غير محددة"])
        if st.button("تحليل أولي واقتراح مواد", type="primary"):
            if not problem.strip():
                st.warning("يرجى وصف المشكلة أولاً.")
            else:
                st.info("هذا الإصدار يستخدم قواعد ترشيح مبسطة، وليس نموذج فهم لغوي مدرّباً. يلزم تأكيد المتطلبات قبل اعتماد أي اختيار.")
                st.write("**ملخص المشكلة:**", problem)
                st.write(f"**مجال الاستخدام:** {application} | **الوسط:** {environment} | **الأولوية:** {priority}")
                candidates = materials.copy()
                if environment == "رطوبة أو ماء":
                    candidates = candidates[candidates["corrosion_note"].str.contains("جيدة|ممتازة", na=False)]
                if priority == "تقليل الوزن":
                    candidates = candidates.sort_values("density_kg_m3")
                elif priority == "مقاومة ميكانيكية":
                    candidates = candidates.sort_values("tensile_strength_mpa", ascending=False)
                elif priority == "مقاومة التآكل":
                    candidates = candidates.sort_values("corrosion_rank", ascending=False)
                elif priority == "خفض التكلفة":
                    candidates = candidates.sort_values("relative_cost_rank")
                st.success("مواد أولية تستحق الدراسة:")
                st.dataframe(candidates[["name_ar","designation","family","density_kg_m3","tensile_strength_mpa","corrosion_note","relative_cost"]].head(5), use_container_width=True, hide_index=True)
                st.warning("هذه قائمة فرز أولية. لا تمثل توصية هندسية نهائية؛ يجب تحديد الحمل، الأبعاد، درجة الحرارة، نوع الفشل، معيار التصميم وحالة المادة.")
    else:
        st.write("أدخل المتطلبات التقنية لفرز المواد وفق قاعدة البيانات.")
        c1,c2,c3 = st.columns(3)
        with c1:
            min_strength = st.number_input("أدنى مقاومة شد مطلوبة (MPa)", min_value=0.0, value=200.0, step=25.0)
            max_density = st.number_input("أقصى كثافة (kg/m³)", min_value=100.0, value=8000.0, step=100.0)
        with c2:
            corrosion = st.selectbox("مقاومة التآكل المطلوبة", ["أي مستوى", "جيدة أو ممتازة"])
            max_cost = st.selectbox("حد التكلفة النسبي", ["أي تكلفة", "منخفض", "متوسط"])
        with c3:
            family = st.multiselect("عائلات المواد", sorted(materials["family"].unique()), default=list(materials["family"].unique()))
        if st.button("فرز المواد حسب المعايير", type="primary"):
            result = materials[
                (materials["tensile_strength_mpa"] >= min_strength) &
                (materials["density_kg_m3"] <= max_density) &
                (materials["family"].isin(family))
            ].copy()
            if corrosion == "جيدة أو ممتازة":
                result = result[result["corrosion_rank"] >= 2]
            if max_cost == "منخفض":
                result = result[result["relative_cost_rank"] <= 2]
            elif max_cost == "متوسط":
                result = result[result["relative_cost_rank"] <= 3]
            st.write(f"عدد النتائج: **{len(result)}**")
            st.dataframe(result[["name_ar","designation","family","density_kg_m3","tensile_strength_mpa","young_modulus_gpa","corrosion_note","relative_cost"]], use_container_width=True, hide_index=True)
            if not result.empty:
                st.download_button("تنزيل نتائج الفرز CSV", result.to_csv(index=False).encode("utf-8-sig"), "material_selection.csv", "text/csv")

with tab2:
    st.header("قاعدة بيانات المواد")
    st.caption("القيم تقريبية وتمثيلية للتجربة التعليمية؛ تختلف باختلاف السبيكة، المعالجة، المنتج والمعيار. استبدلها ببيانات موثقة قبل الاستخدام.")
    query = st.text_input("ابحث باسم المادة أو الرمز أو العائلة")
    view = materials.copy()
    if query:
        mask = view.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)
        view = view[mask]
    st.dataframe(view, use_container_width=True, hide_index=True)
    selected = st.selectbox("عرض بطاقة مادة", materials["designation"].tolist())
    row = materials[materials["designation"] == selected].iloc[0]
    st.subheader(f"{row['name_ar']} — {row['designation']}")
    a,b,c = st.columns(3)
    a.metric("الكثافة", f"{row['density_kg_m3']:,.0f} kg/m³")
    b.metric("مقاومة الشد التقريبية", f"{row['tensile_strength_mpa']:,.0f} MPa")
    c.metric("معامل يونغ", f"{row['young_modulus_gpa']:,.0f} GPa")
    st.write("**الاستخدامات:**", row["applications"])
    st.write("**طرق التصنيع:**", row["processing"])
    st.write("**ملاحظات التآكل:**", row["corrosion_note"])
    st.write("**ملاحظات الاستعمال:**", row["usage_limits"])
    st.write("**المصدر/حالة البيانات:**", row["data_status"])

with tab3:
    st.header("اقتراح مواد بديلة")
    chosen = st.selectbox("اختر المادة الأصلية", materials["designation"].tolist(), key="substitute")
    original = materials[materials["designation"] == chosen].iloc[0]
    st.write(f"المادة الأصلية: **{original['name_ar']} ({chosen})**")
    st.write("حدد ما يجب الحفاظ عليه عند الاستبدال:")
    preserve_strength = st.checkbox("الحفاظ على مقاومة الشد تقريباً", value=True)
    preserve_density = st.checkbox("الحفاظ على الوزن/الكثافة", value=False)
    preserve_corrosion = st.checkbox("الحفاظ على مقاومة التآكل", value=True)
    alternatives = materials[materials["designation"] != chosen].copy()
    alternatives["strength_difference_pct"] = abs(alternatives["tensile_strength_mpa"] - original["tensile_strength_mpa"]) / max(original["tensile_strength_mpa"],1) * 100
    alternatives["density_difference_pct"] = abs(alternatives["density_kg_m3"] - original["density_kg_m3"]) / max(original["density_kg_m3"],1) * 100
    alternatives["corrosion_difference"] = abs(alternatives["corrosion_rank"] - original["corrosion_rank"])
    score = 0
    if preserve_strength: score = score + alternatives["strength_difference_pct"] * 0.5
    if preserve_density: score = score + alternatives["density_difference_pct"] * 0.3
    if preserve_corrosion: score = score + alternatives["corrosion_difference"] * 20
    alternatives["screening_score"] = score
    alternatives = alternatives.sort_values("screening_score")
    st.dataframe(alternatives[["name_ar","designation","family","tensile_strength_mpa","density_kg_m3","corrosion_note","relative_cost","screening_score"]].head(5), use_container_width=True, hide_index=True)
    st.warning("الترتيب هنا فرز أولي مبني على مؤشرات محدودة، وليس إثبات تكافؤ. يجب فحص الصلادة، التعب، المتانة، اللحام، المعالجة، الشكل المنتج، المعايير، وظروف التشغيل قبل الاستبدال.")
    st.write("**ملاحظة توفر:** هذه النسخة لا تتصل بمخزون الموردين. يجب إضافة موردين حقيقيين والتحقق من المخزون والأسعار وتاريخ آخر تحديث.")

with tab4:
    st.header("حساب ميكانيكي أولي — إجهاد الشد المحوري")
    st.write("أدخل القوة ومساحة المقطع لحساب الإجهاد الاسمي ومقارنته بمقاومة الخضوع المدخلة.")
    force = st.number_input("القوة المحورية F (N)", min_value=0.0, value=5000.0, step=500.0)
    area = st.number_input("مساحة المقطع A (mm²)", min_value=0.1, value=100.0, step=10.0)
    yield_strength = st.number_input("مقاومة الخضوع Re (MPa)", min_value=1.0, value=250.0, step=10.0)
    factor = st.number_input("معامل الأمان المطلوب", min_value=1.0, value=2.0, step=0.5)
    stress = force / area
    allowable = yield_strength / factor
    x,y,z = st.columns(3)
    x.metric("الإجهاد الاسمي", f"{stress:.2f} MPa")
    y.metric("الإجهاد المسموح المبسط", f"{allowable:.2f} MPa")
    z.metric("معامل الأمان المحسوب", f"{yield_strength/stress:.2f}" if stress else "—")
    if stress <= allowable:
        st.success("النتيجة الأولية: الإجهاد الاسمي أقل من الإجهاد المسموح وفق هذا النموذج المبسط.")
    else:
        st.error("النتيجة الأولية: الإجهاد الاسمي يتجاوز الإجهاد المسموح وفق هذا النموذج المبسط.")
    st.caption("لا يشمل الحساب تركيز الإجهاد، الانبعاج، التعب، القص، الانحناء، الوصلات، العيوب أو عوامل المعايير. ليس اعتماداً لتصميم حقيقي.")

with tab5:
    st.header("التنبؤ بعمر التعب — باستخدام بيانات تجريبية")
    st.write("هذا الجزء لا يولّد عمراً افتراضياً. يجب رفع ملف تجارب حقيقية يحتوي على الخصائص المدخلة وعدد الدورات حتى الفشل.")
    st.markdown("""
**الأعمدة المطلوبة في CSV:**
- `stress_mpa` : الإجهاد الدوري (MPa)
- `ultimate_strength_mpa` : مقاومة الشد القصوى (MPa)
- `yield_strength_mpa` : مقاومة الخضوع (MPa)
- `temperature_c` : درجة الحرارة (°C)
- `stress_ratio` : نسبة الإجهاد R
- `cycles_to_failure` : عدد الدورات حتى الفشل
""")
    uploaded = st.file_uploader("ارفع ملف تجارب CSV", type=["csv"])
    if uploaded is not None:
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
            from sklearn.pipeline import make_pipeline
            from sklearn.impute import SimpleImputer
            from sklearn.preprocessing import StandardScaler
            from sklearn.compose import ColumnTransformer
            df = pd.read_csv(uploaded)
            required = ["stress_mpa","ultimate_strength_mpa","yield_strength_mpa","temperature_c","stress_ratio","cycles_to_failure"]
            missing = [c for c in required if c not in df.columns]
            if missing:
                st.error("الأعمدة الناقصة: " + ", ".join(missing))
            elif len(df) < 30:
                st.error("عدد السجلات أقل من 30. لا يُنصح بتدريب نموذج موثوق على عينة صغيرة جداً؛ اجمع بيانات أكثر ومتنوعة.")
            else:
                df = df[required].replace([np.inf,-np.inf], np.nan).dropna()
                df = df[(df["cycles_to_failure"] > 0)]
                if len(df) < 30:
                    st.error("عدد السجلات الصالحة بعد التنظيف أقل من 30.")
                else:
                    X = df[required[:-1]]
                    y = np.log10(df["cycles_to_failure"])
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
                    model = make_pipeline(SimpleImputer(strategy="median"), RandomForestRegressor(n_estimators=250, random_state=42, min_samples_leaf=2))
                    model.fit(X_train, y_train)
                    pred = model.predict(X_test)
                    y_actual_cycles = 10 ** y_test
                    y_pred_cycles = 10 ** pred
                    st.subheader("تقييم النموذج على مجموعة اختبار")
                    m1,m2,m3 = st.columns(3)
                    m1.metric("MAE (cycles)", f"{mean_absolute_error(y_actual_cycles,y_pred_cycles):,.0f}")
                    m2.metric("RMSE (cycles)", f"{np.sqrt(mean_squared_error(y_actual_cycles,y_pred_cycles)):,.0f}")
                    m3.metric("R² على log10(N)", f"{r2_score(y_test,pred):.3f}")
                    st.caption("هذه المقاييس تصف أداء النموذج على تقسيم الاختبار فقط؛ يلزم تحقق خارجي حسب المادة ونوع الاختبار.")
                    st.subheader("إدخال حالة جديدة")
                    p1,p2,p3 = st.columns(3)
                    with p1:
                        s = st.number_input("Stress (MPa)", min_value=0.1, value=150.0)
                        uts = st.number_input("Ultimate strength (MPa)", min_value=1.0, value=600.0)
                    with p2:
                        ys = st.number_input("Yield strength (MPa)", min_value=1.0, value=400.0)
                        temp = st.number_input("Temperature (°C)", value=25.0)
                    with p3:
                        ratio = st.number_input("Stress ratio R", min_value=-2.0, max_value=1.0, value=0.1)
                    if st.button("تقدير عدد الدورات"):
                        sample = pd.DataFrame([[s,uts,ys,temp,ratio]], columns=required[:-1])
                        estimate = 10 ** float(model.predict(sample)[0])
                        st.metric("عدد الدورات المتوقع حتى الفشل", f"{estimate:,.0f} cycles")
                        st.warning("تقدير تجريبي خاص بنطاق البيانات المرفوعة فقط. لا تستخدمه لتحديد عمر خدمة أو سلامة قطعة فعلية دون تحقق هندسي مستقل.")
        except Exception as e:
            st.error(f"تعذر معالجة الملف: {e}")

st.divider()
st.caption("MAT-OPTIM AI — Prototype académique. يجب استبدال البيانات التوضيحية بمراجع موثقة والتحقق من كل توصية قبل الاستخدام الصناعي.")
