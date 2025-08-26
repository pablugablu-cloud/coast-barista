# Coast & Barista FIRE — Modern, Simple, Beautiful (Streamlit)
# -----------------------------------------------------------
# - Clean landing hero with quick definitions
# - Minimal inputs on the left, clear metrics on the right
# - Ultra‑clear visuals tied to Coast/Barista (donuts + bullet bar)
# - Uses Streamlit's st.cache_data for speed

import numpy as np
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Coast & Barista FIRE · Monte Carlo", layout="wide")

# ----------------------------- Core Monte Carlo -----------------------------
@st.cache_data
def run_monte_carlo(
    current_age: int,
    coast_age: int,
    retire_age: int,
    life_expectancy: int,
    current_savings: float,
    contrib_full: float,
    contrib_barista: float,
    withdraw_retire: float,
    mean_return: float,
    return_vol: float,
    n_sims: int,
    seed: int | None = None,
):
    """Monte Carlo for Coast-FIRE & Barista-FIRE.
    Returns (final_balances at life_expectancy, retire_balances at retire_age).
    """
    if seed is not None and seed != 0:
        np.random.seed(seed)

    years_total = life_expectancy - current_age
    years_to_retire = retire_age - current_age
    final_balances = np.zeros(n_sims)
    retire_balances = np.zeros(n_sims)

    for i in range(n_sims):
        # --- Full path to life expectancy ---
        bal = float(current_savings)
        for year in range(years_total):
            r = np.random.normal(mean_return / 100.0, return_vol / 100.0)
            bal *= (1 + r)
            age = current_age + year
            if age < coast_age:
                bal += contrib_full
            elif age < retire_age:
                bal += contrib_barista
            else:
                bal -= withdraw_retire
            if bal <= 0:
                bal = 0.0
                break
        final_balances[i] = bal

        # --- Balance at retirement only ---
        bal_ret = float(current_savings)
        for year in range(years_to_retire):
            r = np.random.normal(mean_return / 100.0, return_vol / 100.0)
            bal_ret *= (1 + r)
            age = current_age + year
            if age < coast_age:
                bal_ret += contrib_full
            else:
                bal_ret += contrib_barista
            if bal_ret <= 0:
                bal_ret = 0.0
                break
        retire_balances[i] = bal_ret

    return final_balances, retire_balances

# ----------------------------- Styling (lightweight) -----------------------------
st.markdown(
    """
    <style>
      .hero {padding: 28px 24px; border-radius: 18px; background: radial-gradient(1200px 600px at 0% 0%, #eef6ff 0%, #ffffff 55%); border: 1px solid #e9eef6;}
      .tag {display:inline-block; padding:6px 10px; border-radius:999px; background:#eef6ff; color:#1a64ad; font-weight:600; margin-right:8px;}
      .muted {color:#6b7280}
      .metric-card {padding:16px; border:1px solid #edf2f7; border-radius:14px; background:#ffffff}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------- Hero / Landing -----------------------------
col_hero, = st.columns(1)
with col_hero:
    st.markdown(
        """
        <div class="hero">
          <span class="tag">🔥 Coast & Barista FIRE</span>
          <h2 style="margin:8px 0 4px 0;">See—in one glance—if you can coast or go barista.</h2>
          <p class="muted" style="margin:0">• <b>Coast‑FIRE</b>: investments should grow enough on their own — you only need to earn your living expenses.<br>
          • <b>Barista‑FIRE</b>: part‑time work + smaller contributions still get you to the goal.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------- Inputs -----------------------------
with st.sidebar:
    st.header("Inputs")
    current_age = st.number_input("Current Age", 18, 100, 43)
    coast_age = st.number_input("Coast (Part‑time) Age", current_age, 100, 50)
    retire_age = st.number_input("Full Retirement Age", coast_age, 100, 60)
    life_expectancy = st.number_input("Life Expectancy", retire_age, 120, 85)

    st.divider()
    current_savings = st.number_input("Current Savings ($)", value=1_090_000, step=10_000)
    contrib_full = st.number_input("Annual Savings (Full‑time) ($)", value=24_000, step=1_000)
    contrib_barista = st.number_input("Annual Savings (Barista) ($)", value=5_000, step=1_000)
    withdraw_retire = st.number_input("Annual Retirement Withdrawal ($)", value=95_000, step=1_000)

    st.divider()
    mean_return = st.slider("Expected Annual Return (%)", -5.0, 15.0, 7.5, 0.1)
    return_vol = st.slider("Return Volatility (Std Dev %)", 0.0, 25.0, 10.0, 0.1)

    st.divider()
    n_sims = st.number_input("Number of Simulations", 100, 100_000, 5000, 100)
    seed = st.number_input("Random Seed (optional)", 0)

run = st.sidebar.button("Run simulation", type="primary")

# ----------------------------- Run + Results -----------------------------
if run:
    with st.spinner("Running Monte Carlo…"):
        finals, retires = run_monte_carlo(
            current_age,
            coast_age,
            retire_age,
            life_expectancy,
            current_savings,
            contrib_full,
            contrib_barista,
            withdraw_retire,
            mean_return,
            return_vol,
            n_sims,
            seed if seed != 0 else None,
        )

    # Targets & probabilities
    years_retirement = max(0, life_expectancy - retire_age)
    target = withdraw_retire * years_retirement
    prob_target = float(np.mean(retires >= target))
    prob_survive = float(np.mean(finals > 0))

    # Coast/Barista quick checks
    years_to_retire = max(0, retire_age - current_age)
    coast_balance = current_savings * (1 + mean_return/100.0) ** years_to_retire
    median_retire = float(np.median(retires))

    # Metric cards
    mcol1, mcol2, mcol3 = st.columns(3)
    with mcol1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Chance: on track by retirement", f"{prob_target:.0%}")
        st.markdown('</div>', unsafe_allow_html=True)
    with mcol2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Chance: lasts to life expectancy", f"{prob_survive:.0%}")
        st.markdown('</div>', unsafe_allow_html=True)
    with mcol3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Target need (withdrawals × years)", f"${int(target):,}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Status banners
    coast_ok = coast_balance >= target
    barista_ok = median_retire >= target
    if coast_ok:
        st.success("🎉 Coast‑FIRE: Your current savings alone are expected to grow to your target by retirement.")
    else:
        shortfall_coast = max(0, target - coast_balance)
        st.warning(f"🚧 Not Coast‑FIRE: estimated short by ${shortfall_coast:,.0f} (using average return).")

    if barista_ok:
        st.success("🎉 Barista‑FIRE: With part‑time contributions, you’re on track by retirement (median path).")
    else:
        shortfall_barista = max(0, target - median_retire)
        st.warning(f"🚧 Not Barista‑FIRE: median balance short by ${shortfall_barista:,.0f} at retirement.")

    st.divider()

    # ----------------------------- Ultra-clear visuals -----------------------------
    # (A) Barista-FIRE likelihood — what % of simulations meet the retirement target
    on_track = prob_target
    shortfall = max(0.0, 1.0 - on_track)
    fig_a = go.Figure(go.Pie(
        values=[on_track, shortfall],
        labels=["On track by retirement", "Shortfall"],
        hole=0.6,
        sort=False,
        textinfo="label+percent",
    ))
    fig_a.update_layout(title_text="Barista‑FIRE Likelihood", margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig_a, use_container_width=True)
    st.caption("Barista‑FIRE = part‑time savings until retirement. Green slice = % of simulated futures that reach your target by retirement.")

    # (B) Coast‑FIRE check — compare your 'no more savings' projection to the retirement target
    fig_b = go.Figure()
    fig_b.add_trace(go.Bar(
        x=[coast_balance], y=["Coast projection (no more savings)"],
        orientation="h", name="Coast projection",
        text=[f"${int(coast_balance):,}"], textposition="outside"
    ))
    fig_b.add_vline(x=target, line_dash="dash", line_color="#EF4444")
    fig_b.update_layout(title_text="Coast‑FIRE Check: Current Savings Growth vs Target", xaxis_title="Dollars", yaxis_title="",
                        margin=dict(l=10, r=10, t=60, b=10), showlegend=False)
    st.plotly_chart(fig_b, use_container_width=True)
    if coast_ok:
        st.caption("Your current savings are projected to grow enough on their own to hit the target by retirement.")
    else:
        st.caption(f"You'd be ~${int(max(0, target - coast_balance)):,} short if you stopped saving now. Consider delaying Coast or saving more until Coast.")

    # (C) Portfolio longevity — % of simulations that still have money at life expectancy
    alive = prob_survive
    depleted = max(0.0, 1.0 - alive)
    fig_c = go.Figure(go.Pie(
        values=[alive, depleted],
        labels=["Lasts to life expectancy", "Runs out early"],
        hole=0.6,
        sort=False,
        textinfo="label+percent",
    ))
    fig_c.update_layout(title_text="Portfolio Longevity", margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig_c, use_container_width=True)
    st.caption("Green slice = % of simulated futures where your portfolio still has money at life expectancy.")

    # Explainer
    with st.expander("What do these results mean? (plain English)"):
        st.markdown(
            """
            **Coast‑FIRE** → Your current savings could compound to reach the retirement target without new savings.  
            **Barista‑FIRE** → With smaller, part‑time contributions, you can still be on track by retirement.  
            **Monte Carlo** → We simulate many possible yearly returns (around your average & volatility) to show a range of outcomes.
            """
        )

else:
    st.empty()
    st.write("")
    st.write("")
    st.markdown("**Ready when you are — set your inputs on the left and click _Run simulation_.**")
