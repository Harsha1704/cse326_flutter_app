import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

void main() {
  runApp(const CSE326App());
}

class CSE326App extends StatelessWidget {
  const CSE326App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CSE326 App',
      debugShowCheckedModeBanner: false,
      home: const WebPageView(),
    );
  }
}

class WebPageView extends StatelessWidget {
  const WebPageView({super.key});

  @override
  Widget build(BuildContext context) {
    if (kIsWeb) {
      return const HtmlIframeWidget(); // Web view using iframe
    } else if (Platform.isAndroid || Platform.isIOS) {
      return const WebViewPage(); // Android/iOS native WebView
    } else {
      return const Center(child: Text("Unsupported Platform"));
    }
  }
}

class WebViewPage extends StatefulWidget {
  const WebViewPage({super.key});

  @override
  State<WebViewPage> createState() => _WebViewPageState();
}

class _WebViewPageState extends State<WebViewPage> {
  late final WebViewController _controller;

  @override
  void initState() {
    super.initState();

    // Use 10.0.2.2 for Android emulator to access host machine (Live Server)
    const liveServerUrl = 'http://10.0.2.2:5500/assets/index.html';

    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..loadRequest(Uri.parse(liveServerUrl));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("CSE326 Live Preview"),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => _controller.reload(),
          )
        ],
      ),
      body: SafeArea(
        child: WebViewWidget(controller: _controller),
      ),
    );
  }
}

class HtmlIframeWidget extends StatelessWidget {
  const HtmlIframeWidget({super.key});

  @override
  Widget build(BuildContext context) {
    // Automatically load the live server web view inside an iframe (for web version)
    return const Scaffold(
      body: Center(
        child: SizedBox(
          width: 390,
          height: 844,
          child: HtmlElementView(viewType: 'iframe-html'),
        ),
      ),
    );
  }
}
