# João Vitor Santian

**Back-end Developer · PHP / Laravel** · Curitiba, Brazil

I work on a multi-tenant financial SaaS (budget planning and P&L calculation) for a Canadian company. I took part in migrating the legacy monolith from Zend Framework / PHP 7 to Laravel / PHP 8, and today I handle L3 production support, focused on MySQL performance, asynchronous processing and financial calculation rules.

**Some results:**
- MySQL queries on tables with tens of millions of rows: document lookup from 17.5 min to 12 s, yearly export from ~47 min to ~4 min
- Batch rewrites of N+1 and quadratic routines: planning copy from 50 to 7 min
- 41 async processes running on AWS SQS (FIFO), plus a new one with concurrency lock and 6.3× faster batch deletion

### Stack

![PHP](https://img.shields.io/badge/PHP-777BB4?style=for-the-badge&logo=php&logoColor=white)
![Laravel](https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![AWS SQS](https://img.shields.io/badge/AWS_SQS-FF4F8B?style=for-the-badge&logo=amazonsqs&logoColor=white)
![PHPUnit](https://img.shields.io/badge/PHPUnit-3C9CD7?style=for-the-badge&logo=php&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)

### Featured projects

| Project | What it is | Stack |
|---|---|---|
| [para-onde-foi](https://github.com/Santiann/para-onde-foi) | Personal expense tracker with goals and dashboard, tested and running in production | Laravel, Livewire, PostgreSQL, Pest, Docker |
| [desafio-TORO](https://github.com/Santiann/desafio-TORO) | Sales incentive platform: a scoring engine credits points to sellers while respecting the campaign budget | PHP 8.3 (no framework), MySQL, React/TypeScript, Docker |
| [gerador-de-relatorios](https://github.com/Santiann/teste-desenvolvedor-gerador-de-relatorios) | Billing app with reports built for millions of records | Laravel, Next.js/TypeScript, MySQL, Docker |
| [FCoin](https://github.com/Santiann/Programacao-Distribuida) | Distributed transaction validation with Proof of Stake consensus and concurrent validators | Python, Flask, REST |

### Contact

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/joao-santian)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:joaosantian1@gmail.com)
