# Mettere l'app su un server

Questa guida porta l'app su un piccolo server virtuale (VPS) in Europa. Si fa una volta sola; dopo, ogni merge su `main` aggiorna il server da solo.

## 1. Comprare il server

Un VPS con 2 CPU, 4 GB di RAM e Ubuntu 24.04 basta per iniziare. Per esempio Hetzner Cloud, con data center in Germania o Finlandia. Al momento della creazione aggiungi la tua chiave SSH pubblica, così entri senza password.

Annota l'indirizzo IP del server.

## 2. Preparare il server

Entra con `ssh root@IP_DEL_SERVER` ed esegui:

```bash
# Aggiornamenti e Docker
apt update && apt upgrade -y
curl -fsSL https://get.docker.com | sh

# Firewall: solo SSH, HTTP e HTTPS
ufw allow OpenSSH && ufw allow 80 && ufw allow 443 && ufw --force enable

# Utente dedicato al deploy, che può usare Docker
adduser --disabled-password --gecos "" deploy
usermod -aG docker deploy
mkdir -p /opt/trader-slave && chown deploy:deploy /opt/trader-slave
```

## 3. Scaricare l'app e configurarla

Sempre sul server:

```bash
su - deploy
git clone https://github.com/pittalavito/trader-slave-v2.git /opt/trader-slave
cd /opt/trader-slave
cp .env.example .env
nano .env   # cambia almeno POSTGRES_PASSWORD
docker compose up -d --build
```

Apri `http://IP_DEL_SERVER` nel browser: deve comparire "Trader Slave" con lo stato dell'API "ok".

## 4. Dominio e HTTPS (facoltativo, consigliato)

1. Dal tuo provider del dominio crea un record `A` che punta all'IP del server, per esempio `app.tuodominio.it`.
2. Nel file `.env` del server imposta `DOMAIN=app.tuodominio.it`.
3. Riavvia con `docker compose up -d`.

Caddy ottiene e rinnova da solo il certificato HTTPS.

## 5. Deploy automatico da GitHub

1. Sul tuo computer crea una chiave dedicata al deploy: `ssh-keygen -t ed25519 -f deploy_key -N ""`.
2. Sul server aggiungi la chiave pubblica: incolla il contenuto di `deploy_key.pub` in `/home/deploy/.ssh/authorized_keys` (crea la cartella `.ssh` con permessi 700 e il file con permessi 600, di proprietà dell'utente `deploy`).
3. Su GitHub, in **Settings → Secrets and variables → Actions** del repository, aggiungi:
   - `VPS_HOST`: l'IP o il dominio del server
   - `VPS_USER`: `deploy`
   - `VPS_SSH_KEY`: il contenuto del file `deploy_key` (la chiave privata)

Da quel momento ogni push su `main` esegue il workflow **Deploy**, che entra nel server, scarica il codice nuovo e riavvia i container.

## Comandi utili sul server

```bash
cd /opt/trader-slave
docker compose ps              # stato dei servizi
docker compose logs -f worker  # log del motore dei bot
docker compose logs -f api     # log dell'API
docker compose restart worker  # riavvia il motore
```

## Sicurezza

- Il file `.env` resta solo sul server e non va mai su GitHub.
- Quando collegheremo Kraken, limita le chiavi API all'IP del server e non dare il permesso di prelievo.
- Il wallet Solana dedicato conterrà solo il capitale delle strategie.
