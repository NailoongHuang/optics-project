"""Write the manually assessed evidence record using verified source metadata."""
from pathlib import Path
import json

OUT = Path(__file__).resolve().parent

ASSESSMENTS = {
    "osborne_linden_2004": dict(
        journal="Physical Review A", volume="69", pages="052315", year=2004,
        doi="10.1103/PhysRevA.69.052315",
        relevance="direct-prior-art",
        evidence_location="arXiv PDF pp. 4-6; Eq. (7), Fig. 2, Fig. 3, and the unnumbered third-order broadening formula on p. 6",
        evidence="在均匀Heisenberg环的单激发子空间，将Gaussian调制的格点波包放在波矢编号N/4，亦即ka=pi/2。正文明确指出二阶导数消失后仍须保留三阶色散；图示传播和拖尾振荡，并讨论包宽按N^(1/3)增长。",
        comparison="与当前每个方向的cosine带及pi/2中心Gaussian是直接同类机制。当前二维可分离乘积态同时选择两个方向的该点，不足以构成新的保形原理。",
        inference="将文中归一化环坐标换回格点单位，三阶控制参数对应t/(初始格点宽度)^3；这是标度对应，不是照抄其宽度定义下的数值常数。",
        limits="论文是有限环、高保真传输和有限展宽，非无限时间严格保形；其Airy措辞在本项目宜表述为Airy型高阶色散形变。",
    ),
    "haselgrove_2005": dict(
        journal="Physical Review A", volume="72", pages="062326", year=2005,
        doi="10.1103/PhysRevA.72.062326",
        relevance="encoding-method-and-benchmark",
        evidence_location="arXiv PDF p. 3, Section II and Eqs. (7)-(8); p. 5, Section II discussion and Fig. 2",
        evidence="用发送区到接收区的受限演化算符的最大奇异值和对应右奇异向量优化编码。均匀Heisenberg链例子中，最优单激发编码快速变为近Gaussian的传播波包。",
        comparison="说明任取Gaussian并非优化极限，若研究目标是指定接收窗口和时间的传输，应与SVD最优编码作比较。",
        inference="本项目若只调载波点和Gaussian宽度，尚不能声称最优状态传输。",
        limits="优化的是给定发送/接收区域及时间的通信指标，不等价于要求整段传播始终保形；引用的文件为v2预印本。",
    ),
    "gong_brumer_2007": dict(
        journal="Physical Review A", volume="75", pages="032331", year=2007,
        doi="10.1103/PhysRevA.75.032331",
        relevance="packet-preparation-and-control",
        evidence_location="arXiv PDF pp. 2-3, Eqs. (13)-(15), Fig. 1; pp. 4-5, Figs. 2-3",
        evidence="选取少数格点的相干初态，使Heisenberg链自然产生向两侧传播、色散较慢的波包对。抛物形磁场脉冲可以停止并重新发射波包。",
        comparison="已有从有限自旋控制产生低色散波包、调控运动的研究；比只预设宽Gaussian更接近制备问题。",
        inference="制备效率和控制资源可作为后续应用问题，但本文已经提供一个先例。",
        limits="涉及外场脉冲和量子踢转子对应，不能说与当前无外场自由演化完全相同；停止运动也不自动冻结内部相位。",
    ),
    "apollaro_2012": dict(
        journal="Physical Review A", volume="85", pages="052319", year=2012,
        doi="10.1103/PhysRevA.85.052319",
        relevance="boundary-engineered-transport",
        evidence_location="arXiv PDF pp. 2-3, Eqs. (10)-(17); pp. 8-9, Figs. 10-11 and conclusions",
        evidence="均匀最近邻通道只调两对端部键，使被激发的模式近似相干传播；比较均匀、单参数、双参数与完全工程化通道的波包演化，渐近传输保真度约0.991。",
        comparison="利用近线性色散模式做低展宽传输已有成熟设计；当前周期晶格没有注入和接收界面，因此不同于端到端器件表现。",
        inference="把自由传播动画推进到器件主张时，需要加入端部耦合或制备/接收基准。",
        limits="其最优键强度标度不同于自由Gaussian的宽度标度，不能混用；非完全均匀、无限晶格的逐点保形定理。",
    ),
    "banchi_2013": dict(
        journal="The European Physical Journal Plus", volume="128", pages="137",
        year=2013, doi="10.1140/epjp/i2013-13137-6",
        relevance="review-with-analytical-extension",
        evidence_location="arXiv PDF pp. 6-7, Eq. (17), Eq. (22), Section 3.2; p. 8, XX inflection k0=pi/2",
        evidence="以集中在色散拐点的波包解释弹道量子态传输，区分多格点初态编码与端部工程形成的谱权重，并指出首个非线性谱修正来自三次项。",
        comparison="为本项目的中心波矢选择、高阶展宽和与通信方案的区别提供直接综述入口。",
        inference="综述引用Osborne-Linden与Haselgrove，因此本次向后引文追踪建立了早期到后续工作的连续链路。",
        limits="文中non-linearity指色散关系的非线性，不是相互作用引起的非线性波动方程。",
    ),
    "thompson_2016": dict(
        journal="New Journal of Physics", volume="18", pages="073044",
        year=2016, doi="10.1088/1367-2630/18/7/073044",
        relevance="direct-prior-art-with-error-bound",
        evidence_location="arXiv PDF pp. 9-10, Theorem 4.1 and Corollary 4.1; pp. 23-25, Section 6.3 proof",
        evidence="对均匀XY环上以p0=N/4为中心的Gaussian波包，给出实际演化相对刚性平移的态向量误差界O(t Delta_p^3/N^3)，并将界扩展到多个可交换链的乘积波包。",
        comparison="p0=N/4等价于ka=pi/2；以物理谱宽或格点包宽表达，误差界对应O(t/宽度^3)。高阶误差及乘积结构已有明确处理。",
        inference="本项目数值验证三次寿命标度可作为复现与适用范围核查，不宜单独称新规律。",
        limits="误差界为渐近Gaussian和窄谱条件下的上界；论文为量子计算构造，多个链不等于非可分离二维晶格。",
    ),
    "meier_2025": dict(
        journal="Nature Physics", volume="21", pages="1147-1152", year=2025,
        doi="10.1038/s41567-025-02929-2",
        relevance="recent-application",
        evidence_location="Published full text: Theoretical description near bulk propagation and Optimization results; arXiv PDF p. 5 and Supplementary Section C3b pp. 18-19",
        evidence="自主量子时钟用静态耦合坡道生成波包，在均匀XY链bulk中围绕k0=pi/2传播。正文明确给出E(k)=2g cos(k)，以lambda_l~n^(1/3)平衡三阶形变和到达时间不确定度。",
        comparison="与当前零二阶色散点机制高度一致，说明这一已知机制仍可用于新的器件/信息任务。",
        inference="潜在价值在新应用、约束和性能指标，不在重新发现pi/2处的低展宽传播。",
        limits="这是具有非均匀制备/吸收区和耗散复位环节的理论时钟模型，不是我们自由二维Gaussian的同一实验。arXiv仅v1，已另核对2025期刊正文。",
        published_fulltext="https://pmc.ncbi.nlm.nih.gov/articles/PMC12263443/",
    ),
}

QUERIES = [
    "Gaussian wave packet spin chain pi/2 dispersion quantum communication Osborne Linden",
    "spin chain Gaussian wavepacket cubic dispersion N 1/3 quantum state transfer",
    "Heisenberg chain nonspreading Gaussian wave packets pi/2",
    '"Gaussian" "spin chain" "π/2"',
    '"Ballistic quantum state transfer" Banchi arxiv',
    '"spin chain" "wave packet" "third" dispersion',
    'Haselgrove "Optimal state encoding" arxiv',
    '"Time independent universal computing with spin chains" arxiv',
    '"Precision is not limited by the second law" arxiv authors',
    '"Optimal dynamics for quantum-state" Banchi 2011',
    '"spin chain" "wave packet" "inflection" 2024 2025 2026',
    '"Gaussian wavepacket" "pi/2" spin',
    '"magnon" "cubic dispersion" wavepacket',
    '"spin chain" "nonspreading" "wave packet"',
    'site:journals.aps.org "Controlled quantum-state transfer" "032331"',
    'site:journals.aps.org "99%-fidelity" "052319"',
]


def main():
    source = json.loads((OUT / "download_manifest.json").read_text(encoding="utf-8"))
    records = []
    for raw in source["sources"]:
        record = raw | ASSESSMENTS[raw["key"]]
        record["pdf_pages"] = raw["pages"]
        record["title"] = raw["metadata"]["citation_title"][0]
        record["authors"] = raw["metadata"]["citation_author"]
        record["publication_url"] = "https://doi.org/" + record["doi"]
        records.append(record)
    (OUT / "papers.json").write_text(json.dumps(
        dict(date="2026-10-20", records=records), ensure_ascii=False, indent=2),
        encoding="utf-8")
    bib = []
    for r in records:
        bib.append("@article{" + r["key"] + ",\n" + "\n".join([
            "  author = {" + " and ".join(r["authors"]) + "},",
            "  title = {" + r["title"] + "},",
            "  journal = {" + r["journal"] + "},",
            "  volume = {" + r["volume"] + "},",
            "  pages = {" + r["pages"] + "},",
            "  year = {" + str(r["year"]) + "},",
            "  doi = {" + r["doi"] + "},",
            "  eprint = {" + raw_id(r["arxiv_version"]) + "},",
            "  archivePrefix = {arXiv},",
        ]) + "\n}")
    (OUT / "references.bib").write_text("\n\n".join(bib) + "\n", encoding="utf-8")
    log = dict(
        date="2026-10-20", language="English primary literature; Chinese assessment",
        scope="Uniform cosine-band single-excitation packets near ka=pi/2, higher-order dispersion, and spin-chain transport applications",
        sources_used=["Web search discovery", "Official arXiv version histories and PDFs",
                      "APS and IOP publisher records", "Nature Physics full text via publisher and PMC"],
        queries=QUERIES,
        citation_chasing=[
            "Banchi 2013 references 44 and 45 -> Osborne-Linden 2004 and Haselgrove 2005",
            "Thompson 2016 Theorem 4.1 -> direct cubic-dispersion error bound",
            "Meier 2025 body and Supplementary C3b -> current application and scaling"],
        deduplication="By DOI and arXiv base ID; versions count as one paper",
        exclusions=[
            "Flat bands and stationary localization are not evidence of propagating low-spreading packets",
            "Nonlinear spin solitons and externally confined Gaussian revivals have different mechanisms",
            "Electron orbital packets, Stern-Gerlach beams, and atomic internal-spin packets are not direct magnetic single-magnon precedents",
            "Long-range coupling designs with exactly linear bands change the Hamiltonian and do not establish this nearest-neighbor effect"],
        stopping_condition="Stopped after direct earliest cosine-band precedent, quantitative error-bound treatment, encoding/control/engineering benchmarks, and a verified 2025 application were covered; broad variants increasingly returned other systems",
        limitations="Bounded multi-source topic search, not exhaustive citation index coverage or a novelty certificate. No configured Semantic Scholar/OpenAlex adapter was used. Relevant passages were inspected; not every page of every paper was closely read.",
    )
    (OUT / "search-log.json").write_text(json.dumps(
        log, ensure_ascii=False, indent=2), encoding="utf-8")


def raw_id(identifier):
    return identifier.rsplit("v", 1)[0]


if __name__ == "__main__":
    main()
