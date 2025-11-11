"""
High-Stakes Test Scenario Library
Comprehensive collection of real-world scenarios for system validation
"""
from dataclasses import dataclass
from typing import List


@dataclass
class HighStakesScenario:
    """Test scenario with expected output metrics"""
    id: str
    title: str
    description: str
    domain: str
    expected_assumptions: int
    expected_fragilities: int
    complexity: str  # 'low', 'medium', 'high'


# ============================================================================
# GEOPOLITICAL SCENARIOS
# ============================================================================

GEOPOLITICAL_SCENARIOS = [
    HighStakesScenario(
        id="geo_001",
        title="Taiwan Strait Military Escalation",
        description="""
        China has announced large-scale military exercises surrounding Taiwan,
        citing new US arms sales as provocation. The exercises involve over
        100 warships and aircraft operating within Taiwan's Air Defense
        Identification Zone. US has responded by sending two carrier strike
        groups to the region under the banner of "freedom of navigation."
        Both sides assert commitment to "defending their interests at all costs."

        Markets are reacting nervously with Taiwan semiconductor stocks dropping
        12% and tech stocks globally down 5% on supply chain concerns. Japan
        has convened emergency cabinet meetings and is considering activating
        mutual defense provisions. South Korea remains officially neutral but
        has increased military readiness. ASEAN nations are calling for
        de-escalation but have no enforcement mechanism.

        Key assumptions: Both sides prefer controlled escalation to war.
        Supply chains can be rapidly rerouted. Diplomatic channels remain open.
        Economic interdependence will prevent military conflict. International
        institutions can mediate effectively.
        """,
        domain="geopolitical",
        expected_assumptions=12,
        expected_fragilities=8,
        complexity="high"
    ),

    HighStakesScenario(
        id="geo_002",
        title="Middle East Oil Supply Disruption",
        description="""
        Coordinated drone attacks on major oil infrastructure in Saudi Arabia
        have reduced global supply by 4 million barrels per day (4% of global
        supply). Three refineries and two export terminals are offline with
        repairs estimated at 3-6 weeks. Iran denies involvement but regional
        intelligence suggests state-sponsored actors. Oil prices surge 30% to
        $110/barrel in 24 hours, triggering inflation concerns globally.

        US President convenes National Security Council to discuss options
        including Strategic Petroleum Reserve release (potentially 30 million
        barrels) and military response. European nations scrambling for
        alternative energy sources as winter approaches. China increases
        purchases from Russia and Iran. India facing fiscal crisis with
        subsidy costs exploding.

        Assumptions: Repairs will proceed on schedule. Markets will stabilize
        after initial shock. Alternative suppliers can fill gaps. No further
        attacks will occur. Financial system can absorb price shock. Political
        pressure for military response can be managed.
        """,
        domain="geopolitical",
        expected_assumptions=10,
        expected_fragilities=7,
        complexity="high"
    ),

    HighStakesScenario(
        id="geo_003",
        title="NATO Article 5 Ambiguity in Cyberattack",
        description="""
        A major cyberattack has crippled critical infrastructure across three
        Baltic states (Estonia, Latvia, Lithuania) simultaneously. Power grids,
        banking systems, and telecommunications are down. Attribution analysis
        suggests state-sponsored actors from Russia, but evidence is not
        conclusive. Lithuania has invoked NATO Article 5 collective defense,
        creating unprecedented crisis: no kinetic attack has occurred, but
        economic damage exceeds $50 billion and rising.

        NATO convenes emergency session. US and UK support Article 5 activation.
        France and Germany urge caution, noting attribution difficulties.
        Turkey proposes diplomatic solution. Russia denies involvement, calls
        accusations "provocative." China watches carefully, noting precedent
        for Taiwan scenarios. Global financial markets down 3% on uncertainty.

        Assumptions: NATO consensus can be achieved. Cyber attribution is
        reliable enough for Article 5. Russia will not escalate to kinetic
        warfare. Allies will support collective response. International law
        clearly covers cyber warfare. Economic damage can be contained.
        """,
        domain="geopolitical",
        expected_assumptions=11,
        expected_fragilities=9,
        complexity="high"
    ),
]


# ============================================================================
# ECONOMIC SCENARIOS
# ============================================================================

ECONOMIC_SCENARIOS = [
    HighStakesScenario(
        id="econ_001",
        title="Major Bank Liquidity Crisis",
        description="""
        The fourth-largest US bank has announced inability to meet withdrawal
        demands after $40 billion in deposits (25% of total) fled in 48 hours
        following rumors of exposure to commercial real estate defaults. Stock
        down 75% in pre-market trading. Federal Reserve holds emergency weekend
        meetings. Treasury Secretary preparing prime-time address to nation.

        Contagion concerns spreading to three regional banks with similar
        exposure profiles. Total assets at risk: $250 billion. FDIC insurance
        covers only $250,000 per account, leaving large depositors exposed.
        Silicon Valley and startup ecosystem panicking as payroll accounts
        frozen. Credit markets seizing up as counterparty risk escalates.

        Assumptions: Federal backstop will be provided. Contagion can be
        contained. Deposit insurance limits are adequate. Commercial real
        estate defaults are manageable. Bank executives acted prudently.
        Regulatory oversight was sufficient. Market confidence can be restored
        quickly. Moral hazard concerns can be ignored in crisis.
        """,
        domain="economic",
        expected_assumptions=15,
        expected_fragilities=10,
        complexity="high"
    ),

    HighStakesScenario(
        id="econ_002",
        title="Sovereign Debt Default Cascade",
        description="""
        Argentina has defaulted on $65 billion in sovereign debt, triggering
        immediate contagion fears. Credit default swaps are paying out, causing
        three European hedge funds to declare force majeure. Rating agencies
        downgrading eight emerging market nations. Capital flight from developing
        economies reaching $200 billion in one week.

        IMF convenes emergency meeting but lacks resources for full bailout.
        China offers bilateral assistance with "development partnership" strings
        attached. US Treasury concerned about precedent but divided on response.
        Brazil, Turkey, and South Africa seeing bond yields spike 400+ basis
        points. Pension funds globally taking heavy losses on EM debt holdings.

        Assumptions: Contagion can be contained to emerging markets. Advanced
        economies are insulated. IMF has sufficient firepower. Political will
        exists for coordinated response. Currency markets will stabilize.
        Social unrest in affected nations can be managed. Chinese intervention
        won't create strategic dependencies.
        """,
        domain="economic",
        expected_assumptions=13,
        expected_fragilities=8,
        complexity="high"
    ),

    HighStakesScenario(
        id="econ_003",
        title="Supply Chain Semiconductor Shortage",
        description="""
        An earthquake in Taiwan has damaged TSMC's leading-edge fabrication
        plants, eliminating 40% of global advanced chip production capacity
        for 6-12 months. Automotive, smartphone, AI hardware, and defense
        industries facing immediate shutdowns. Apple delays iPhone launch.
        GM announces 50% production cuts. NVIDIA cannot fulfill AI chip orders
        worth $15 billion.

        Emergency White House meeting on national security implications. Pentagon
        concerned about F-35 production delays. Commerce Department exploring
        emergency Defense Production Act invocation. Intel and Samsung offered
        government subsidies to accelerate alternative capacity but need 18+
        months. Chip prices surge 300%. Scalping and gray markets emerging.

        Assumptions: TSMC repairs will complete on schedule. Alternative
        suppliers can partially fill gaps. Industries can absorb delays.
        Price increases won't trigger broader inflation. National security
        needs can be prioritized. Geopolitical rivals won't exploit vulnerability.
        Downstream economic impacts are manageable.
        """,
        domain="economic",
        expected_assumptions=12,
        expected_fragilities=9,
        complexity="high"
    ),
]


# ============================================================================
# OPERATIONAL SCENARIOS
# ============================================================================

OPERATIONAL_SCENARIOS = [
    HighStakesScenario(
        id="ops_001",
        title="Cloud Infrastructure Cascade Failure",
        description="""
        AWS US-East-1 region experiencing total outage affecting 40% of
        internet services. Root cause: cascading failure from routine
        maintenance error. Estimated recovery: 8-12 hours. Netflix, Disney+,
        Reddit, Slack, and thousands of SaaS applications offline. E-commerce
        transactions worth $2 billion per hour frozen. Smart home devices
        non-functional. Ring doorbells, Nest thermostats, connected medical
        devices offline.

        Amazon incident response overwhelmed. No ETA for full restoration.
        Multi-region failover not working as documented. Backup systems also
        dependent on US-East-1. Corporate customers unable to switch to Azure
        or GCP due to tight coupling. Media covering "single point of failure"
        concerns. Regulatory hearings being scheduled.

        Assumptions: Recovery is possible within 24 hours. Data is not
        corrupted. Redundancy systems will eventually activate. Customer data
        is secure. Financial losses can be absorbed. Regulatory response won't
        be punitive. Market confidence in cloud model will survive.
        """,
        domain="operational",
        expected_assumptions=11,
        expected_fragilities=7,
        complexity="medium"
    ),

    HighStakesScenario(
        id="ops_002",
        title="Hospital System Ransomware Attack",
        description="""
        A coordinated ransomware attack has encrypted patient records and
        disabled operational systems across a 15-hospital healthcare network
        serving 2 million patients. Electronic health records inaccessible.
        Emergency rooms diverting critical cases. Surgeries cancelled. Lab
        results unavailable. Pharmacy systems down. Ransom demand: $50 million
        in cryptocurrency, 72-hour deadline.

        FBI investigating but cautioning against payment. Backup systems also
        encrypted due to connected networks. Recovery from offline backups
        estimated at 2-3 weeks. Patients with chronic conditions unable to
        access medication histories. Cancer treatments delayed. ICU patients
        being manually monitored. Medical staff using paper charts.

        Assumptions: Patient care quality can be maintained manually. No
        deaths will result from system outage. Ransom payment will result in
        decryption. Backups are viable. Attackers won't leak patient data.
        Insurance will cover losses. Regulatory penalties will be waived.
        Hospital reputation will recover.
        """,
        domain="operational",
        expected_assumptions=14,
        expected_fragilities=11,
        complexity="high"
    ),

    HighStakesScenario(
        id="ops_003",
        title="Air Traffic Control System Failure",
        description="""
        FAA's NextGen air traffic control system has crashed nationwide due to
        software bug in recent update. All US airspace grounded. 5,000+ flights
        canceled affecting 1.2 million passengers. International flights to US
        being turned back. Backup systems unable to handle full traffic load.
        Recovery timeline: unknown, potentially 24-48 hours.

        Economic impact: $50 million per hour in direct costs. Cascading effects
        on hotels, car rentals, business meetings. Medical transplant organs
        not reaching recipients. Military aircraft operating on separate systems
        but commercial airspace restrictions limiting training. Airlines losing
        $200 million per day. Insurance claims mounting.

        Assumptions: Software can be rolled back successfully. Backup systems
        will handle essential traffic. Safety is not compromised. Recovery
        won't require complete system rebuild. Public confidence in air travel
        will recover quickly. Economic damage can be absorbed. Liability is
        limited.
        """,
        domain="operational",
        expected_assumptions=10,
        expected_fragilities=8,
        complexity="high"
    ),
]


# ============================================================================
# SOCIAL SCENARIOS
# ============================================================================

SOCIAL_SCENARIOS = [
    HighStakesScenario(
        id="social_001",
        title="Viral Misinformation During Elections",
        description="""
        Two weeks before national elections, a deepfake video of a leading
        candidate apparently confessing to corruption has gone viral, reaching
        200 million views in 36 hours. Forensic analysis confirms it's fake,
        but detection tools are not publicly accessible. Social media platforms
        struggling to remove copies appearing faster than moderation can respond.
        Foreign state actors suspected but not confirmed.

        Opposition party refusing to denounce fake, saying "questions deserve
        answers." Polls showing 15-point swing in 48 hours. Election integrity
        organizations overwhelmed. Courts being petitioned to delay elections.
        Justice Department investigating but unlikely to conclude before vote.
        International observers expressing concerns. Civil society groups
        planning protests.

        Assumptions: Truth will eventually prevail. Voters can discern fake
        from real. Election infrastructure is secure. Social media companies
        are acting in good faith. Foreign interference can be prevented.
        Democratic institutions are resilient. Post-election challenges can be
        resolved peacefully.
        """,
        domain="social",
        expected_assumptions=12,
        expected_fragilities=9,
        complexity="high"
    ),

    HighStakesScenario(
        id="social_002",
        title="Public Health Crisis Communication Breakdown",
        description="""
        A novel infectious disease with 2% mortality rate is spreading rapidly
        in three major cities. Initial public health messaging emphasized low
        risk, but now recommends mask mandates and possible lockdowns. Public
        trust in health authorities collapsed after messaging reversal.
        Compliance with health measures at 30%.

        Social media filled with competing narratives. Celebrity doctors
        promoting unproven treatments. Political figures calling health measures
        "government overreach." Hospital ICUs reaching capacity. Supply chain
        for treatments and PPE strained. Economic activity contracting as people
        self-isolate despite official guidance. Schools closing despite official
        recommendations to stay open.

        Assumptions: Scientific consensus can be communicated effectively.
        Public will follow expert guidance. Political polarization won't
        interfere. Healthcare system capacity is adequate. Economic support
        systems can cushion impact. Vaccine development will proceed quickly.
        International coordination is possible.
        """,
        domain="social",
        expected_assumptions=13,
        expected_fragilities=10,
        complexity="high"
    ),
]


# ============================================================================
# TECHNOLOGICAL SCENARIOS
# ============================================================================

TECHNOLOGICAL_SCENARIOS = [
    HighStakesScenario(
        id="tech_001",
        title="AI Model Alignment Failure at Scale",
        description="""
        A widely deployed AI model used for financial trading, content
        moderation, and medical diagnosis has been discovered to have a
        systematic bias that escaped testing. The model makes decisions that
        appear correct individually but create harmful patterns at scale.
        Financial losses from trading errors: $2 billion. Content moderation
        failures led to radicalization pipeline. Medical misdiagnoses affecting
        50,000+ patients.

        Model developer claims procedures were followed. Regulators investigating
        but lack technical expertise. Industry rushing to audit similar systems.
        Lawsuits being filed. Insurance companies reassessing AI liability
        coverage. Calls for AI development moratorium. International regulatory
        cooperation discussions beginning.

        Assumptions: Problem can be fixed with model update. Affected systems
        can be identified. Damage is limited to discovered cases. Testing
        methodologies exist to prevent recurrence. Liability frameworks are
        adequate. Public trust in AI can be restored. Alternative systems can
        fill gaps during remediation.
        """,
        domain="technological",
        expected_assumptions=14,
        expected_fragilities=11,
        complexity="high"
    ),
]


# ============================================================================
# ENVIRONMENTAL SCENARIOS
# ============================================================================

ENVIRONMENTAL_SCENARIOS = [
    HighStakesScenario(
        id="env_001",
        title="Cascading Grid Failure During Heat Wave",
        description="""
        Record-breaking heat wave (115°F+) across southwestern US for 14
        consecutive days. Electricity demand exceeds grid capacity by 40%.
        Rolling blackouts planned for 2-4 hours, but grid instability causing
        unplanned cascading failures lasting 12+ hours. 50 million people
        affected. Hospitals on backup generators. Water treatment plants
        struggling. Food spoilage widespread.

        Death toll rising (200+ heat-related). Elderly and poor most affected.
        Cooling centers overwhelmed. FEMA deploying resources but logistics
        strained. Climate change activists demanding emergency action. Energy
        companies defending infrastructure investment levels. Insurance industry
        reassessing coverage models. Migration from affected regions beginning.

        Assumptions: Heat wave will end within forecast window. Grid can be
        restored without major rebuilds. Emergency response systems are adequate.
        Social order will be maintained. Healthcare system can handle surge.
        Economic impacts are temporary. Similar events remain rare.
        """,
        domain="environmental",
        expected_assumptions=11,
        expected_fragilities=9,
        complexity="high"
    ),
]


# ============================================================================
# AGGREGATE COLLECTIONS
# ============================================================================

ALL_SCENARIOS = (
    GEOPOLITICAL_SCENARIOS +
    ECONOMIC_SCENARIOS +
    OPERATIONAL_SCENARIOS +
    SOCIAL_SCENARIOS +
    TECHNOLOGICAL_SCENARIOS +
    ENVIRONMENTAL_SCENARIOS
)

HIGH_COMPLEXITY_SCENARIOS = [s for s in ALL_SCENARIOS if s.complexity == "high"]
MEDIUM_COMPLEXITY_SCENARIOS = [s for s in ALL_SCENARIOS if s.complexity == "medium"]

# Scenario counts
print(f"""
📊 Test Scenario Library Statistics:
- Total scenarios: {len(ALL_SCENARIOS)}
- Geopolitical: {len(GEOPOLITICAL_SCENARIOS)}
- Economic: {len(ECONOMIC_SCENARIOS)}
- Operational: {len(OPERATIONAL_SCENARIOS)}
- Social: {len(SOCIAL_SCENARIOS)}
- Technological: {len(TECHNOLOGICAL_SCENARIOS)}
- Environmental: {len(ENVIRONMENTAL_SCENARIOS)}
- High complexity: {len(HIGH_COMPLEXITY_SCENARIOS)}
- Medium complexity: {len(MEDIUM_COMPLEXITY_SCENARIOS)}
""")
