# caseStudyQuant
Case Study Quant Position for Optimize Energy


### Running the code ###

1. Make sure you have all dependencies installed.

```bash
pip install -r requirements.txt
```

2. Run config.py first to set the in and out directories first, just in case you want to change the directories. 

In here you can also change any "environment variables" that you want to change.

3. Run price download first to download the prices for the respective hourly data. You can change dates to download in the descarga_precio_diario.py file.

```bash
python descarga_precio_diario.py
```

4. Run optimization by executing the optimization.py file. You can change the parameters to optimize in the optimization.py file.

```bash
python optimization.py
```

5. Run the plotting by executing the generador_graficas.py file. 4 graphs will be generated in the graficas directory.

```bash
python generador_graficas.py
```

6. Run the dash app by executing the app.py file.

```bash
python app.py
```





