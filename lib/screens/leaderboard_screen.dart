import 'package:flutter/material.dart';
import '../services/leaderboard_service.dart';
import '../tahmin_oyunu.dart'; // GameMode

class LeaderboardScreen extends StatefulWidget {
  const LeaderboardScreen({super.key});

  @override
  State<LeaderboardScreen> createState() => _LeaderboardScreenState();
}

class _LeaderboardScreenState extends State<LeaderboardScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final LeaderboardService _leaderboardService = LeaderboardService();

  @override
  void initState() {
    super.initState();
    // 3 Tabs: Kolay, Zor, God Mod
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade900,
      appBar: AppBar(
        title: const Text("Dünya Sıralaması 🌍"),
        backgroundColor: Colors.black,
        foregroundColor: Colors.white,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.orange,
          labelColor: Colors.orange,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(text: "KOLAY"),
            Tab(text: "ZOR"),
            Tab(text: "GOD MOD"),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildLeaderboardList(GameMode.easy),
          _buildLeaderboardList(GameMode.hard),
          _buildLeaderboardList(GameMode.god),
        ],
      ),
    );
  }

  Widget _buildLeaderboardList(GameMode mode) {
    return FutureBuilder<List<Map<String, dynamic>>>(
      future: _leaderboardService.getTopScores(mode),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator(color: Colors.orange));
        }
        
        if (snapshot.hasError) {
          return Center(
            child: Text(
              "Bağlantı Hatası!\nİnternetinizi kontrol edin.",
              style: TextStyle(color: Colors.red.shade300, fontSize: 16),
              textAlign: TextAlign.center,
            ),
          );
        }

        final scores = snapshot.data ?? [];

        if (scores.isEmpty) {
          return const Center(
            child: Text(
              "Henüz skor yok.\nİlk rekoru sen kır! 🏆",
              style: TextStyle(color: Colors.white54, fontSize: 18),
              textAlign: TextAlign.center,
            ),
          );
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: scores.length,
          itemBuilder: (context, index) {
            final entry = scores[index];
            final rank = index + 1;
            final isTop3 = rank <= 3;
            
            Color rankColor = Colors.white;
            if (rank == 1) rankColor = Colors.yellow;
            if (rank == 2) rankColor = Colors.grey.shade300;
            if (rank == 3) rankColor = Colors.orange.shade300;

            return Card(
              color: Colors.grey.shade800,
              margin: const EdgeInsets.only(bottom: 10),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(15),
                side: isTop3 ? BorderSide(color: rankColor, width: 2) : BorderSide.none,
              ),
              child: ListTile(
                leading: Container(
                  width: 40,
                  height: 40,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isTop3 ? rankColor.withOpacity(0.2) : Colors.black26,
                  ),
                  child: Text(
                    "#$rank",
                    style: TextStyle(
                      color: rankColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                    ),
                  ),
                ),
                title: Text(
                  entry['username'],
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
                  ),
                ),
                trailing: Text(
                  "${entry['score']}",
                  style: const TextStyle(
                    color: Colors.greenAccent,
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            );
          },
        );
      },
    );
  }
}
