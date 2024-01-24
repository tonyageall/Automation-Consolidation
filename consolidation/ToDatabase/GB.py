from neo4j import GraphDatabase

class Neo4jConnector:
    def __init__(self, uri, username, password):
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None

    def connect(self):
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            return self  # Return self to allow method chaining
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Neo4j database: {str(e)}")

    def test_connection(self):
        if self.driver is None:
            raise ConnectionError("Connection is not established. Call connect() method first.")
            
        with self.driver.session() as session:
            result = session.run("RETURN 'Connected' AS status")
            record = result.single()
            return record['status']

    def close(self):
        if self.driver is not None:
            self.driver.close()


class ProjectScraper:
    def __init__(self, df):
        self.data = df  # Assign the DataFrame to an instance attribute

    def scrape_project_input(self):
        Project = self.data['Project'].values
        START = self.data['Start'].values[0]
        END = self.data['End'].values[0]
        SOW = self.data['SOW'].values[0]
        GENES = self.data['Gene'].values
        GENESeq = self.data['GeneSeq'].values[0]
        PROTEINNAME = self.data['Protein'].values[0]
        Protein_Leader = self.data['ProtSeq'].values
        Protein_noLeader = self.data['ProtSeqNoLeader'].values

        MW_kDa = self.data['MW_kDa'].values
        MW_kDa_noLeader = self.data['MW_kDa_noLeader'].values
        PI = self.data['PI'].values
        PI_noLeader = self.data['PI_noLeader'].values

        Charge = self.data['Charge_neutral'].values
        Charge_neutral_noLeader = self.data['Charge_neutral_noLeader'].values

        ExtCoef = self.data['ExtCoef'].values
        ExtCoef_noLeader = self.data['ExtCoef_NoLeader'].values

        GENE_LeaderPROTEIN = {
            GENES[0]: [
                Protein_Leader[0],
                MW_kDa[0],
                PI[0],
                Charge[0],
                ExtCoef[0]
            ]
        }

        Gene_NoLeaderProtein = {
            GENES[0]: [
                Protein_noLeader[0],
                MW_kDa_noLeader[0],
                PI_noLeader[0],
                Charge_neutral_noLeader[0],
                ExtCoef_noLeader[0]
            ]
        }

        return Project, START, END, SOW, GENES, PROTEINNAME, GENESeq, GENE_LeaderPROTEIN, Gene_NoLeaderProtein


def create_project(tx, project, startDATE, endDate, SOW):
    tx.run("CREATE (Pr:Project {Project: $project, Start: $startDATE, End: $endDate, SOW: $SOW})",
           project=project, startDATE=startDATE, endDate=endDate, SOW=SOW)
    

    
def create_gene_to_projects(tx, project, GeneID, GeneSeq, protID, MW_Leader, pI, OD, netCharge,
                             MW_noLeader, pI_noLeader, OD_noLeader, netCharge_noLeader,
                             MWseq, MWnLseq):
    tx.run("MATCH (pr:Project {Project: $project}) "
           "MERGE (pr)-[:ScreensFor]->(g:GeneID {gene: $GeneID, geneSeq:$GeneSeq, proteinID: $protID, MW: $MW_Leader, pI: $pI, OD: $OD, nchrg: $netCharge, MWNL: $MW_noLeader, pInL: $pI_noLeader, ODnL: $OD_noLeader, nchrgnL: $netCharge_noLeader, MWseq: $MWseq, MWnLseq: $MWnLseq})",
           project=project, GeneID=GeneID, GeneSeq=GeneSeq, protID=protID, MW_noLeader=MW_noLeader, pI_noLeader=pI_noLeader,
           OD_noLeader=OD_noLeader, netCharge_noLeader=netCharge_noLeader, MW_Leader=MW_Leader, pI=pI,
           OD=OD, netCharge=netCharge, MWseq=MWseq, MWnLseq=MWnLseq)
