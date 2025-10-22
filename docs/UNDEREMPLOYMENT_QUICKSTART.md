# Underemployment Analysis - Quick Start Guide

This guide will help you run the underemployment and career trajectories analysis in under 5 minutes.

## Prerequisites

- Python 3.8+
- College Scorecard data (see below for download instructions)

## Step 1: Get the Data

### Option A: Use Existing Data (If Available)
If you already have College Scorecard data at:
```
/Users/isaiah/Projects/data25/collegedata/collegescorecard.csv
```
You can proceed directly to Step 2.

### Option B: Download Fresh Data
1. Visit: https://collegescorecard.ed.gov/data/
2. Click "Download Data"
3. Download the "Most Recent Institution-Level Data"
4. Save the CSV file to: `data/raw/collegescorecard.csv`

**Quick Download (Command Line):**
```bash
# Create data directory
mkdir -p data/raw

# Download latest data (URL may change - check website)
# Note: This is a large file (~200MB+)
curl -o data/raw/collegescorecard.csv \
  "https://ed-public-download.app.cloud.gov/downloads/Most-Recent-Cohorts-Institution.csv"
```

## Step 2: Run the Analysis

### Using Command Line (Recommended for First Run)

```bash
# Run with your data path
python run_underemployment_analysis.py --data-path data/raw/collegescorecard.csv
```

**With causal analysis export:**
```bash
python run_underemployment_analysis.py \
  --data-path data/raw/collegescorecard.csv \
  --export-causal
```

### Using Python API

Create a new Python script or Jupyter notebook:

```python
from src.analysis import UnderemploymentAnalyzer, load_college_scorecard_data

# Load data
df = load_college_scorecard_data('data/raw/collegescorecard.csv')

# Initialize analyzer
analyzer = UnderemploymentAnalyzer(df)

# Run complete analysis
results = analyzer.run_complete_analysis()

# View results
print("\nField-Level Risk (Top 10):")
print(results['field_risk'].head(10))

print("\nCompletion Gradient:")
print(results['completion_gradient'])

print("\nScarring Analysis:")
print(f"High-risk institutions: {results['scarring_analysis']['high_risk_count']:,}")
```

### Using Jupyter Notebook (Interactive)

```bash
# Launch Jupyter
jupyter lab

# Open: notebooks/05_underemployment_analysis.ipynb
# Update the data path in cell 2
# Run all cells
```

## Step 3: View Results

After running the analysis, check the `reports/` directory:

```
reports/
├── underemployment_analysis_YYYYMMDD_HHMMSS.txt
└── detailed_results/
    ├── field_risk_YYYYMMDD_HHMMSS.csv
    ├── completion_gradient_YYYYMMDD_HHMMSS.csv
    ├── institution_effects_YYYYMMDD_HHMMSS.csv
    └── socioeconomic_patterns_YYYYMMDD_HHMMSS.csv
```

## What You'll Get

### Console Output
- Summary statistics (institution count, median earnings, etc.)
- Top 10 fields by underemployment risk
- Earnings by completion rate quartiles
- Institution type comparisons
- Socioeconomic stratification patterns
- Career trajectory scarring statistics

### Report Files
- **Text report**: Comprehensive findings in markdown format
- **CSV files**: Detailed results for each analysis component
- **Causal data** (if --export-causal used): Dataset prepared for IV/DiD analysis

## Understanding the Results

### Key Metrics

**Underemployment Risk**: Proportion of institutions where graduates have low earnings relative to degree level (bottom 25th percentile)

**Completion Gradient**: Relationship between 6-year completion rates and median earnings 10 years after entry

**Scarring Indicator**: Institutions with concerning patterns:
- Completion rate < 30%, OR
- Median earnings < $30,000, OR  
- Repayment rate < 40%

### Typical Findings

Based on ~7,700 institutions:
- **Liberal Arts/Humanities**: 20-25% underemployment risk
- **Engineering/STEM**: 1-3% underemployment risk
- **Earnings gap**: $10,000-15,000 between high/low completion quartiles
- **For-profit penalty**: 20-30 point gap in outcomes vs. nonprofits
- **High-risk institutions**: 50-60% of total institutions

## Troubleshooting

### "Data file not found"
- Check file path is correct
- Verify file exists: `ls -lh data/raw/collegescorecard.csv`
- Download data from https://collegescorecard.ed.gov/data/

### "No module named 'src.analysis'"
- Ensure you're running from repository root
- Check Python path: `export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"`

### "KeyError: 'PCIP01'" or similar
- Your data file may be from a different year with different columns
- The analyzer handles missing columns gracefully
- Some analyses may be skipped if key columns are missing

### Memory issues with large files
- College Scorecard files can be large (500MB+ uncompressed)
- Ensure at least 2GB free RAM
- Consider using a subset of columns if needed

## Next Steps

### Explore Results
- Open detailed CSV files in Excel/Python/R
- Compare across years if you have multi-year data
- Examine specific institutions of interest

### Run Causal Analysis
- Export dataset with --export-causal flag
- Use R/Stata/Python for IV/DiD estimation
- Control for confounders (location, selectivity, demographics)

### Customize Analysis
- Modify field groupings in `underemployment_analyzer.py`
- Adjust risk thresholds for scarring indicators
- Add new metrics or visualizations

### Integration with Other Analyses
- Combine with BLS employment data for labor market context
- Link to NCES enrollment trends
- Merge with geographic/demographic data

## Advanced Usage

### Subset Analysis
```python
# Analyze only 4-year public institutions
df_public = df[df['CONTROL'] == 1]
analyzer = UnderemploymentAnalyzer(df_public)
results = analyzer.run_complete_analysis()
```

### Custom Risk Thresholds
```python
# Modify scarring indicator
df['CUSTOM_RISK'] = (
    (df['C150_4_POOLED_SUPP'] < 0.25) |  # Lower completion threshold
    (df['MD_EARN_WNE_P10'] < 35000)       # Higher earnings threshold
).astype(int)
```

### Field-Specific Deep Dive
```python
# Analyze just STEM fields
stem_fields = ['PCIP11', 'PCIP14', 'PCIP15', 'PCIP26', 'PCIP27', 'PCIP40']
field_risk = analyzer.analyze_field_level_risk()
stem_risk = field_risk.loc[['Computer Science', 'Engineering', 'Biological Sciences', 'Mathematics', 'Physical Sciences']]
print(stem_risk)
```

## Getting Help

- Review full documentation: `UNDEREMPLOYMENT_INTEGRATION.md`
- Check function docstrings: `help(UnderemploymentAnalyzer)`
- Review example notebook: `notebooks/05_underemployment_analysis.ipynb`
- Check original research: `~/Projects/data25/PhD_Research_Questions.md`

## Citation

If using this analysis in research:

```
Underemployment and Career Trajectories Analysis Module
Labor Dynamics Analysis Project
https://github.com/kamrawr/labor-dynamics-analysis
```

---

**Time to run:** ~30 seconds to 2 minutes (depending on data size)  
**Output size:** ~500KB-2MB reports + visualizations  
**Data required:** College Scorecard CSV (~200MB-500MB)
