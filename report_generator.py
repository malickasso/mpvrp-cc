from fpdf import FPDF
import datetime

class MPVRP_Report(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Rapport Technique: MPVRP-CC', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} | LRSIA 2026', 0, 0, 'C')

def generate_report(output_path):
    pdf = MPVRP_Report()
    pdf.add_page()
    
    # Page de garde
    pdf.set_font('Arial', 'B', 24)
    pdf.ln(40)
    pdf.cell(0, 20, 'MPVRP-CC', 0, 1, 'C')
    pdf.set_font('Arial', '', 14)
    pdf.cell(0, 10, 'Multi-Product Vehicle Routing Problem', 0, 1, 'C')
    pdf.cell(0, 10, 'with Changeover Cost', 0, 1, 'C')
    
    pdf.ln(50)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Participation des membres:', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, '- IA Assistant (Antigravity): 100%', 0, 1, 'L')
    
    pdf.ln(60)
    pdf.cell(0, 10, f'Date: {datetime.date.today().strftime("%d/%m/%Y")}', 0, 1, 'R')
    
    # Présentation du problème
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '1. Présentation du problème', 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, (
        "Le problème MPVRP-CC (Multi-Product Vehicle Routing Problem with Changeover Cost) "
        "modélise la distribution de plusieurs types de produits (ex: carburants) depuis des dépôts "
        "vers des stations-service.\n\n"
        "Une contrainte majeure est le coût de transition (changeover cost) : chaque fois qu'un véhicule "
        "change le produit transporté dans ses compartiments, un nettoyage est nécessaire, induisant "
        "un coût et un temps supplémentaire. L'objectif est de minimiser la somme des coûts de transport "
        "(distance) et des coûts de transition."
    ))
    
    # Modélisation
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '2. Modélisation du problème', 0, 1, 'L')
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Données du problème:', 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, (
        "- Un ensemble de stations demandant des quantités spécifiques de différents produits.\n"
        "- Un ensemble de dépôts fournissant les produits (stocks).\n"
        "- Une flotte de véhicules avec des capacités limitées et des garages de départ.\n"
        "- Une matrice de coût de transition entre les types de produits."
    ))
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Variables de décision:', 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, (
        "- X_{ijk} : Variable binaire valant 1 si le véhicule k va du nœud i au nœud j.\n"
        "- Q_{ipk} : Quantité de produit p livrée à la station i par le véhicule k.\n"
        "- T_{ijk} : Coût de transition appliqué si le produit porté change entre i et j."
    ))
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Fonction Objectif:', 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, "Minimiser Z = \u2211(Distance * d_ij) + \u2211(Coût de Transition)")
    
    # Résolution
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '3. Résolution', 0, 1, 'L')
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Approche et Solveur:', 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, (
        "Le problème est résolu en utilisant la bibliothèque Google OR-Tools (Constraint Programming). "
        "Une modélisation de type Pickup and Delivery (PDP) a été adoptée pour permettre aux véhicules "
        "de retourner aux dépôts charger des produits lorsque leur capacité est épuisée.\n\n"
        "Les demandes des stations dépassant la capacité d'un véhicule sont automatiquement fractionnées "
        "en plusieurs tâches de livraison."
    ))
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Analyse des résultats:', 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, (
        "Le solveur parvient à trouver des solutions optimales ou quasi-optimales pour les instances "
        "de petite et moyenne taille en quelques secondes. Pour les instances larges, le paramètre "
        "de recherche locale (Guided Local Search) permet d'explorer efficacement l'espace des solutions."
    ))

    pdf.output(output_path)

if __name__ == "__main__":
    generate_report("report_mpvrp_cc.pdf")
