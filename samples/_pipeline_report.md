# PDF QC Comparison Report

- Markup (source of truth): `samples/markup_doc.pdf`
- Proxy (verified): `samples/proxy_doc.pdf`
- Pages compared: 2
- Total differences: 19

## Summary

| Category | Count |
| --- | --- |
| Missing content | 3 |
| Additional content | 1 |
| Changed content | 2 |
| Changed values | 3 |
| Changed dates | 0 |
| Changed percentages | 2 |
| Table discrepancies | 8 |

## Detailed Differences

### Missing content (3)

- **Location:** Page 1
  - Expected: Dear Eaton Vance Fund Shareholder:
  - Actual:   _(none)_
- **Location:** Page 1
  - Expected: BROADRIDGE INVESTOR DELIVERY BLURB
  - Actual:   _(none)_
- **Location:** Page 2
  - Expected: If you have any questions regarding this information, please contact your investment advisor or an Eaton Vance Investor Services associate at 1-866-328-6681.
  - Actual:   _(none)_

### Additional content (1)

- **Location:** Page 1
  - Expected: _(none)_
  - Actual:   8.49% Cumulative total return at NAV for the fiscal year through January 31, 2024° 2 28% Cumulative fiscal year to date distribution rate as a percentage of NAV as of January 31, 20244 0.71% 1 Average annual total return at NAV represents the change in NAV of the Fund, with all distributions reinvested, for the 5-year period ended on January 31, 2024.

### Changed content (2)

- **Location:** Page 1
  - Expected: Start typing here.
  - Actual:   == Eaton Vance Dear Eaton Vance Fund Shareholder:
- **Location:** Page 2
  - Expected: FOR DUPLEX, TYPE HERE NO ACTION IS REQUIRED ON YOUR PART.
  - Actual:   NO ACTION IS REQUIRED ON YOUR PART.

### Changed values (3)

- **Location:** Page 1
  - Expected: 4 Cumulative fiscal year distribution rate for the period from the beginning of its fiscal year to January 31, 2024 measured on the dollar value of distributions in the year-to-date period as a percentage of the Fund's NAV as of January 31, 2024.
  - Actual:   * Cumulative fiscal year distribution rate for the period from the beginning of its fiscal year to January 31, 2024 measured on the dollar value of distributions in the year-to-date period as a percentage of the Fund's NAV as of January 31, 2024.
  - Note:     ['4', '31,', '2024', '31,', '2024'] -> ['31,', '2024', '31,', '2024']
- **Location:** Page 2
  - Expected: LOGO & RETURN ADDRESS WILL AUTOMATICALLY PRINT HERE For Duplex, continue typing here.
  - Actual:   Broadridge' BROADRIDGE-PROXY SERVICES "1 51 MERCEDES WAY mG EDGEWOOD NY 11717 JOHN DOE 51 MERCEDES WAY EDGEWOOD, NY 11717 If you have any questions regarding this information, please contact your investment advisor or an Eaton Vance Investor Services associate at 1-866-328-6681.
  - Note:     [] -> ['1', '51', '11717', '51', '11717', '1', '-866', '-328', '-6681']
- **Location:** Page 2
  - Expected: Eaton Vance Tax-Managed Buy-Write Opportunities Fund February 29, 2024
  - Actual:   Eaton Vance Tax-Managed Buy-Write Opportunities Fund February 29, 2024 Tud-ZTZ00N A82BL2
  - Note:     ['29,', '2024'] -> ['29,', '2024', '00', '82', '2']

### Changed percentages (2)

- **Location:** Page 1
  - Expected: Eaton Vance Tax-Managed Buy-Write Opportunities Fund Cumulative % of the Cumulative Current % of Current Distributions for the Distributions for the Fiscal Source Distribution Distribution Fiscal Year-to-Date1 Year-to-Date1 Net Investment Income $0.0022 2.3% $0.0040 2.1% Net Realized Short-Term $0.0000 0.0% $0.0000 0.0% Capital Gains Net Realized Long-Term $0.0000 0.0% $0.0000 0.0% Capital Gains Return of Capital or Other $0.0927 97.7% $0.1858 97.9% Capital Source(s) Total per common share $0.0949 100.0% $0.1898 100.0% 1 The Fund's fiscal year is January 1, 2024 to December 31, 2024 IMPORTANT DISCLOSURE:
  - Actual:   Eaton Vance Tax-Managed Buy-Write Opportunities Fund Cumulative % of the Cumulative Current % of Current Distributions for the Distributions for the Fiscal Source Distribution Distribution Fiscal Year-to-Date' Year-to-Date' Net Investment Income $0.0022 2.3% $0.0040 2.1% Net Realized Short-Term Capital Gains $0.0000 0.0% $0.0000 0.0% Net Realized Long-Term Capital Gains $0.0000 0.0% $0.0000 0.0% Return of Capital or Other Capital Source(s) Total per common share $0.0949 100.0% $0.1898 100.0% $0.0927 97.7% $0.1858 97.9% 1 The Fund's fiscal year is January 1, 2024 to December 31, 2024 IMPORTANT DISCLOSURE:
  - Note:     ['2.3%', '2.1%', '0.0%', '0.0%', '0.0%', '0.0%', '97.7%', '97.9%', '100.0%', '100.0%'] -> ['2.3%', '2.1%', '0.0%', '0.0%', '0.0%', '0.0%', '100.0%', '100.0%', '97.7%', '97.9%']
- **Location:** Page 1
  - Expected: Average annual total return at NAV for the 5-year period ended on January 31, 20241 8.89% Annualized current distribution rate expressed as a percentage of NAV as of January 31, 20242 8.49% Cumulative total return at NAV for the fiscal year through January 31, 20243 2.28% Cumulative fiscal year to date distribution rate as a percentage of NAV as of January 31, 20244 0.71% 1 Average annual total return at NAV represents the change in NAV of the Fund, with all distributions reinvested, for the 5-year period ended on January 31, 2024.
  - Actual:   Average annual total return at NAV for the 5-year period ended on January 31, 2024' 8.89% Annualized current distribution rate expressed as a percentage of NAV as of January 31, 2024?
  - Note:     ['8.89%', '8.49%', '2.28%', '0.71%'] -> ['8.89%']

### Table discrepancies (8)

- **Location:** Page 1 Table 1
  - Expected: Start typing here. ⏎ Dear Eaton Vance Fund Shareholder: ⏎ This notice provides shareholders of the Eaton Vance Tax-Managed Buy-Write Opportunities Fund (NYSE: ETV) ⏎ with important information concerning the distribution declared in February 2024. You are receiving this notice as ⏎ a requirement of the Fund’s managed distribution plan (Plan). The Board of Trustees approved the ⏎ implementation of the Plan to make monthly cash distributions to common shareholders, stated in terms of a fixed ⏎ amount per common share. This information is sent to you for informational purposes only and is an ⏎ estimate of the sources of the February distribution. It is not determinative of the tax character of the Fund’s ⏎ distributions for the 2024 calendar year. ⏎ The amounts and sources of distributions reported in this notice are estimates, are not being provided for tax ⏎ reporting purposes and the distribution may later be determined to be from other sources including realized short- ⏎ term gains, long-term gains, to the extent permitted by law, and return of capital. The actual amounts and sources ⏎ for tax reporting purposes will depend upon the Fund’s investment experience during the remainder of its fiscal ⏎ year and may be subject to changes based on tax regulations. The Fund will send you a Form 1099-DIV for the ⏎ calendar year that will tell you how to report these distributions for federal income tax purposes. ⏎ Distribution Period: February 2024 ⏎ Distribution Amount per Common Share: $0.0949 ⏎ The following table sets forth an estimate of the sources of the Fund’s February distribution and its cumulative ⏎ distributions paid this fiscal year to date. Amounts are expressed on a per common share basis and as a ⏎ percentage of the distribution amount. ⏎ Eaton Vance Tax-Managed Buy-Write Opportunities Fund ⏎ Cumulative % of the Cumulative ⏎ Current % of Current Distributions for the Distributions for the Fiscal ⏎ Source Distribution Distribution Fiscal Year-to-Date1 Year-to-Date1 ⏎ Net Investment Income $0.0022 2.3% $0.0040 2.1% ⏎ Net Realized Short-Term ⏎ $0.0000 0.0% $0.0000 0.0% ⏎ Capital Gains ⏎ Net Realized Long-Term ⏎ $0.0000 0.0% $0.0000 0.0% ⏎ Capital Gains ⏎ Return of Capital or Other ⏎ $0.0927 97.7% $0.1858 97.9% ⏎ Capital Source(s) ⏎ Total per common share $0.0949 100.0% $0.1898 100.0% ⏎ 1 The Fund’s fiscal year is January 1, 2024 to December 31, 2024 ⏎ IMPORTANT DISCLOSURE: You should not draw any conclusions about the Fund’s investment performance ⏎ from the amount of this distribution or from the terms of the Fund’s Plan. The Fund estimates that it has ⏎ distributed more than its income and net realized capital gains; therefore, a portion of your distribution may be a ⏎ return of capital. A return of capital may occur for example, when some or all of the money that you invested in ⏎ the Fund is paid back to you. A return of capital distribution does not necessarily reflect the Fund’s investment ⏎ performance and should not be confused with ‘yield’ or ‘income.’ The amounts and sources of distributions ⏎ reported in this Notice are only estimates and are not being provided for tax reporting purposes. The actual ⏎ amounts and sources of the amounts for accounting and/or tax reporting purposes will depend upon the Fund’s ⏎ investment experience during the remainder of its fiscal year and may be subject to changes based on tax ⏎ regulations. The Fund will send you a Form 1099-DIV for the calendar year that will tell you how to report these ⏎ distributions for federal income tax purposes. ⏎ Set forth in the table below is information relating to the Fund’s performance based on its net asset value (NAV) ⏎ for certain periods. ⏎ Average annual total return at NAV for the 5-year period ended on January 31, 20241 8.89% ⏎ Annualized current distribution rate expressed as a percentage of NAV as of January 31, 20242 8.49% ⏎ Cumulative total return at NAV for the fiscal year through January 31, 20243 2.28% ⏎ Cumulative fiscal year to date distribution rate as a percentage of NAV as of January 31, 20244 0.71% ⏎ 1 Average annual total return at NAV represents the change in NAV of the Fund, with all distributions reinvested, ⏎ for the 5-year period ended on January 31, 2024. ⏎ 2 The annualized current distribution rate is the cumulative distribution rate annualized as a percentage of the ⏎ Fund's NAV as of January 31, 2024. ⏎ 3 Cumulative total return at NAV is the percentage change in the Fund's NAV for the period from the beginning of ⏎ its fiscal year to January 31, 2024 including distributions paid and assuming reinvestment of those distributions. ⏎ 4 Cumulative fiscal year distribution rate for the period from the beginning of its fiscal year to January 31, 2024 ⏎ measured on the dollar value of distributions in the year-to-date period as a percentage of the Fund's NAV as of ⏎ January 31, 2024.
  - Actual:   _(none)_
  - Note:     table missing
- **Location:** Page 1 Table 2
  - Expected: This notice provides shareholders of the Eaton Vance Tax-Managed Buy-Write Opportunities Fund (NYSE: ETV) ⏎ with important information concerning the distribution declared in February 2024. You are receiving this notice as ⏎ a requirement of the Fund’s managed distribution plan (Plan). The Board of Trustees approved the ⏎ implementation of the Plan to make monthly cash distributions to common shareholders, stated in terms of a fixed ⏎ amount per common share. This information is sent to you for informational purposes only and is an ⏎ estimate of the sources of the February distribution. It is not determinative of the tax character of the Fund’s ⏎ distributions for the 2024 calendar year. ⏎  ⏎ The amounts and sources of distributions reported in this notice are estimates, are not being provided for tax ⏎ reporting purposes and the distribution may later be determined to be from other sources including realized short- ⏎ term gains, long-term gains, to the extent permitted by law, and return of capital. The actual amounts and sources ⏎ for tax reporting purposes will depend upon the Fund’s investment experience during the remainder of its fiscal ⏎ year and may be subject to changes based on tax regulations. The Fund will send you a Form 1099-DIV for the ⏎ calendar year that will tell you how to report these distributions for federal income tax purposes.
  - Actual:   _(none)_
  - Note:     table missing
- **Location:** Page 1 Table 3
  - Expected: The following table sets forth an estimate of the sources of the Fund’s February distribution and its cumulative ⏎ distributions paid this fiscal year to date. Amounts are expressed on a per common share basis and as a ⏎ percentage of the distribution amount.
  - Actual:   _(none)_
  - Note:     table missing
- **Location:** Page 1 Table 4
  - Expected: Eaton Vance Tax-Managed Buy-Write Opportunities Fund ⏎ Cumulative % of the Cumulative ⏎ Current % of Current Distributions for the Distributions for the Fiscal ⏎ Source Distribution Distribution Fiscal Year-to-Date1 Year-to-Date1 ⏎ Net Investment Income $0.0022 2.3% $0.0040 2.1% ⏎ Net Realized Short-Term ⏎ $0.0000 0.0% $0.0000 0.0% ⏎ Capital Gains ⏎ Net Realized Long-Term ⏎ $0.0000 0.0% $0.0000 0.0% ⏎ Capital Gains ⏎ Return of Capital or Other ⏎ $0.0927 97.7% $0.1858 97.9% ⏎ Capital Source(s) ⏎ Total per common share $0.0949 100.0% $0.1898 100.0%
  - Actual:   _(none)_
  - Note:     table missing
- **Location:** Page 1 Table 5
  - Expected:  ⏎ Set forth in the table below is information relating to the Fund’s performance based on its net asset value (NAV) ⏎ for certain periods.
  - Actual:   _(none)_
  - Note:     table missing
- **Location:** Page 1 Table 6
  - Expected: Average annual total return at NAV for the 5-year period ended on January 31, 20241 | 8.89% ⏎ Annualized current distribution rate expressed as a percentage of NAV as of January 31, 20242 | 8.49% ⏎ Cumulative total return at NAV for the fiscal year through January 31, 20243 | 2.28% ⏎ Cumulative fiscal year to date distribution rate as a percentage of NAV as of January 31, 20244 | 0.71%
  - Actual:   _(none)_
  - Note:     table missing
- **Location:** Page 2 Table 1
  - Expected:  |  ⏎  | 
  - Actual:   _(none)_
  - Note:     table missing
- **Location:** Page 2 Table 2
  - Expected:  ⏎ 
  - Actual:   _(none)_
  - Note:     table missing
