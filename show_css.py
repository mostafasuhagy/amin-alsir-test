f = open('amin_alsir_client_dashboard.html', encoding='utf-8').read()
i = f.find(':root')
print(f[i:i+300])
