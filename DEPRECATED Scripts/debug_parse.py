from prepare_dictionary import parse_line
import json

line11 = '11: HAJDUT,",-I m. sh. -Ë, -ËT bised. Vjedhës: cub, kusar: kaçak. Fem. “Ë, GJA sh. -Ë, -ET. Hajdut xhepash. Hajdut malesh. Fole (strehë) hajdutësh. k Gjeti hajduti thesin (u poq hajduti me thesin). fj. u., keq. gjeti tenxherja kapakun, gjeti rrasa vegshin. HAJDUTÇE ndajf. bised. Hajdutërisht (edhe përd. mb.). Hyri hajdutçe. Valle (këngë) hajdutçe. HAKËRROHEM'

entries = parse_line(line11)
for e in entries:
    print(json.dumps(e, ensure_ascii=False))
