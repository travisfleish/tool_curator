import { Pool } from "pg";

const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT,
});

export async function POST(req) {
  try {
    const { email } = await req.json();
    if (!email) {
      return new Response(JSON.stringify({ error: "Email is required" }), { status: 400 });
    }

    await pool.query("INSERT INTO newsletter_subscribers (email) VALUES ($1) ON CONFLICT (email) DO NOTHING", [email]);

    return new Response(JSON.stringify({ message: "Subscription successful" }), { status: 200 });
  } catch (err) {
    console.error("Database error:", err);
    return new Response(JSON.stringify({ error: "Database error" }), { status: 500 });
  }
}
