#Generate a Windows PowerShell script to download the full dataset from the Bureau of Transport Statistics

with open('downlaods.ps1', 'w') as file:
    for i in range(1987, 2021):
        for j in range(1,13):
            filename = 'On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{}_{}.zip'.format(i,j)
            site = "https://transtats.bts.gov/PREZIP/{}".format(filename)
            file.write('Invoke-WebRequest {} -o {}\n'.format(site, filename))