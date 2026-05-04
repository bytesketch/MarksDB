```
┌───────────────────────────────┐
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
│░█▀▄▀█░▄▄▄░░▄░░░█░▄░▄▄░█▀▄░█▀▄░│
│░█░▀░█░█░█░░█▀▀░█▀▄░█▄░█░█░█▀▄░│
│░▀░░░▀░▀▀▀▀░▀░░░▀░▀░▄█░▀▀░░▀▀░░│
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
│░Created░By░Ali░Ahmad░░░░░░░░░░│
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
└───────────────────────────────┘
```

### How to ?

#### Step 0: Make `server` executable

```bash
chmod +x server # Linux/macOS only
```

#### Step 1: Initialize environment and set up dependencies

```bash
./server --init
```

#### Step 2: Configure informations

```bash
./server --configure
```

#### Step 3: Inject root to MySQL

```bash
./server --inject-mysql
```

#### Step 4: Start server

```bash
./server --start [port=8080]
```

#### Now visit

```url
http://localhost:8080/
```

or the URL given by Flask.

##### Example URL Flask will give

```log
 * Serving Flask app 'server'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:8080
Press CTRL+C to quit
```

The URL here is **http://127.0.0.1:8080**
