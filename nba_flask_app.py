from flask import Flask, render_template, request, jsonify
import psycopg2
import json

app = Flask(__name__)

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host='db.fveuqriftywqcqhoujzc.supabase.co',
        database='postgres',
        user='postgres',
        password='MacGruber6969#',
        port=5432
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/players')
def get_players():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get filters from query parameters
    position = request.args.get('position', 'All')
    team = request.args.get('team', 'All')
    min_ppg = float(request.args.get('min_ppg', 0))
    
    # Build query
    query = "SELECT * FROM nba_stats_2025 WHERE points_per_game >= %s"
    params = [min_ppg]
    
    if position != 'All':
        query += " AND position = %s"
        params.append(position)
    
    if team != 'All':
        query += " AND team = %s"
        params.append(team)
    
    query += " ORDER BY points_per_game DESC"
    
    cursor.execute(query, params)
    columns = [desc[0] for desc in cursor.description]
    results = cursor.fetchall()
    
    # Convert to list of dicts
    players = []
    for row in results:
        players.append(dict(zip(columns, row)))
    
    cursor.close()
    conn.close()
    
    return jsonify(players)

@app.route('/api/filters')
def get_filters():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT position FROM nba_stats_2025 ORDER BY position")
    positions = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT team FROM nba_stats_2025 ORDER BY team")
    teams = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'positions': positions,
        'teams': teams
    })

@app.route('/api/stats')
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_players,
            ROUND(AVG(points_per_game)::numeric, 1) as avg_ppg,
            ROUND(AVG(rebounds_per_game)::numeric, 1) as avg_rpg,
            ROUND(AVG(assists_per_game)::numeric, 1) as avg_apg
        FROM nba_stats_2025
    """)
    
    stats = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return jsonify({
        'total_players': stats[0],
        'avg_ppg': float(stats[1]),
        'avg_rpg': float(stats[2]),
        'avg_apg': float(stats[3])
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
