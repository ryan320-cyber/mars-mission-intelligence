# Scientific Methodology & Planetary Mathematics

Mathematical, physical, and statistical documentation for Mars Mission Intelligence.

## 1. Martian Ephemeris & Solar Longitude ($L_s$)
Mars has an orbital eccentricity of $e = 0.0934$, significantly higher than Earth ($e = 0.0167$). Consequently, solar flux varies by over 45% between perihelion ($206.7 \times 10^6\text{ km}$) and aphelion ($249.2 \times 10^6\text{ km}$).

We calculate the Martian Season directly from Solar Longitude ($L_s$, degrees $0^\circ$ to $360^\circ$):
- **$0^\circ \le L_s < 90^\circ$**: Northern Spring / Southern Autumn (Vernal Equinox at $0^\circ$)
- **$90^\circ \le L_s < 180^\circ$**: Northern Summer / Southern Winter (Aphelion at $L_s \approx 71^\circ$)
- **$180^\circ \le L_s < 270^\circ$**: Northern Autumn / Southern Spring (Perihelion approach at $L_s \approx 251^\circ$, Global Dust Season)
- **$270^\circ \le L_s < 360^\circ$**: Northern Winter / Southern Summer (Southern Summer Solstice at $270^\circ$)

---

## 2. Statistical Analysis & Boundary Layer Physics

### Barometric Scale Height Equation
The vertical distribution of atmospheric pressure in a hydrostatic planetary atmosphere is governed by:
$$P(z) = P_0 \exp\left(-\frac{z}{H}\right)$$
where $H$ is the atmospheric scale height:
$$H = \frac{k_B T}{m g} \approx \frac{R_{\text{specific}} T}{g}$$
On Mars, with mean temperature $T \approx 210\text{ K}$, mean molecular weight $m \approx 43.34\text{ g/mol}$ (95.32% $\text{CO}_2$), and surface gravity $g = 3.72\text{ m/s}^2$:
$$H \approx 11.1\text{ km}$$
This explains why Gale Crater (elevation $-4.5\text{ km}$) systematically measures surface pressure 40 to 60 Pa higher than Elysium Planitia (elevation $-2.6\text{ km}$).

### Non-Parametric Hypothesis Testing
Because atmospheric pressure time series exhibit seasonal periodicities that violate bivariate normality assumptions, we utilize the two-sided **Mann-Whitney U Test** for cross-mission comparisons:
$$U_1 = R_1 - \frac{n_1(n_1 + 1)}{2}$$
Effect size is quantified using the rank-biserial correlation:
$$r = 1 - \frac{2U}{n_1 n_2}$$

---

## 3. Dual-Mode Anomaly Intelligence

### Univariate: Robust Modified Z-Score
Standard Z-scores based on sample mean and standard deviation are heavily biased by extreme events (such as planet-encircling dust storms). We use the Median Absolute Deviation (MAD):
$$\text{MAD} = \text{median}\left(|x_i - \tilde{x}|\right)$$
$$\text{Modified } Z_i = \frac{0.6745(x_i - \tilde{x})}{\text{MAD}}$$
Values with $|Z_i| \ge 3.0$ are flagged as anomalies.

### Multivariate: Isolation Forest
To detect anomalous joint physical states where no individual variable is an extreme outlier, we train an `IsolationForest` ensemble ($n=120$ estimators) over the state vector:
$$\mathbf{X} = [T_{\text{max}}, T_{\text{min}}, \Delta T_{\text{diurnal}}, P_{\text{surface}}]$$
The anomaly score $s(x, n)$ evaluates tree path length $h(x)$:
$$s(x, n) = 2^{-\frac{\mathbb{E}(h(x))}{c(n)}}$$
where $c(n)$ is the average path length of unsuccessful searches in a Binary Search Tree.

---

## 4. Martian Environmental Challenge Index (MECI)
The MECI is an engineering challenge index ($0 - 100$) reflecting environmental volatility and hardware stress:
$$MECI = w_1 F_{\text{thermal}} + w_2 F_{\text{pressure}} + w_3 F_{\text{anomaly}} + w_4 F_{\text{season}}$$
where weights are strictly defined:
- $w_1 = 0.35$ (Thermal stress: diurnal swing fatigue on mechanical joints and batteries)
- $w_2 = 0.25$ (Barometric instability: rapid day-to-day pressure change rate)
- $w_3 = 0.25$ (Multivariate anomaly intensity from Isolation Forest)
- $w_4 = 0.15$ (Seasonal dust forcing proximity to perihelion $L_s \in [180^\circ, 320^\circ]$)

Classification tiers:
- **0 – 30**: LOW
- **31 – 60**: MODERATE
- **61 – 80**: HIGH
- **81 – 100**: EXTREME

---

## 5. Machine Learning Validation & Explainability
- **Chronological Split**: Train (first 70%), Validation (next 15%), Test (final 15%).
- **Baselines**:
  - Persistence: $\hat{y}_t = y_{t-1}$
  - Rolling 7-Sol Mean: $\hat{y}_t = \frac{1}{7} \sum_{i=1}^7 y_{t-i}$
- **ML Models**: Ridge Regression ($\alpha=10.0$) and Random Forest Regressor ($n=100$, $\text{max\_depth}=6$).
- **Explainability**: Permutation feature importances and slice-based seasonal error breakdowns.
