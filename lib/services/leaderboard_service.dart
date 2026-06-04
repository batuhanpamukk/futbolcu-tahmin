import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/foundation.dart';
import '../tahmin_oyunu.dart'; // For GameMode enum

class LeaderboardService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  // Collection reference
  CollectionReference get _scoresCollection => _firestore.collection('scores');

  /// Adds a new high score to Firestore
  Future<void> addScore({
    required String username,
    required int score,
    required GameMode mode,
  }) async {
    try {
      await _scoresCollection.add({
        'username': username,
        'score': score,
        'mode': mode.name, // 'easy', 'hard', 'god'
        'timestamp': FieldValue.serverTimestamp(),
        'platform': defaultTargetPlatform.name, // android, ios, etc.
      });
      debugPrint("Score added successfully: $score for $username in ${mode.name}");
    } catch (e) {
      debugPrint("Error adding score: $e");
      rethrow;
    }
  }

  /// Fetches top 20 scores for a specific mode
  Future<List<Map<String, dynamic>>> getTopScores(GameMode mode) async {
    try {
      QuerySnapshot snapshot = await _scoresCollection
          .where('mode', isEqualTo: mode.name)
          .orderBy('score', descending: true) // Highest score first
          .limit(20)
          .get();

      return snapshot.docs.map((doc) {
        final data = doc.data() as Map<String, dynamic>;
        return {
          'username': data['username'] ?? 'Anonymous',
          'score': data['score'] ?? 0,
          // 'timestamp': data['timestamp'], // Optional: show date
        };
      }).toList();
    } catch (e) {
      debugPrint("Error fetching leaderboard: $e");
      return [];
    }
  }
}
