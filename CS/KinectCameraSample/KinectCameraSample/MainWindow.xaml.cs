using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Globalization;
using System.Linq;
using System.Text;
using System.IO;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using Microsoft.Kinect;
using Microsoft.Kinect.Toolkit;
using Microsoft.Speech.AudioFormat;
using Microsoft.Speech.Recognition;

// これはmaster ブランチ

namespace KinectCameraSample
{
    /// <summary>
    /// MainWindow.xaml の相互作用ロジック
    /// </summary>
    public partial class MainWindow : Window
    {
        // --- field ---------------------------------------------------------------------------------------------
        // 深度情報を使用するかどうかのフラグ．開発用
        private bool TEST_DEPTHFLAG = false;


        // Kinect センサーからの画像情報を受け取るバッファ
        private byte[] pixelBuffer = null;

        // Kinect センサーからの深度情報を受け取るバッファ
        private short[] depthBuffer = null;

        // Kinect センサーからの骨格情報を受け取るバッファ
        private Skeleton[] skeletonBuffer = null;

        // データ収集用の骨格のバッファ
        private Skeleton teacherBuffer = null;

        // データ収集用の物体位置のバッファ
        private double[][] boxBuffer = null;

        // 物体位置のバッファに持たせる情報数

            private int boxFeaturesNum = 3;

        // 物体数
        private int boxNum = 3;

        // 画面に表示するタイマー (フレーム単位)
        private int capTimer = -90;

        // データ取得フラグ．タイマーに応じて設定する
        private bool dataFlag = false;

        // 深度情報の各点に対する画像情報上の座標
        private ColorImagePoint[] clrPntBuffer = null;

        // 深度情報で背景を覆う画像のデータ
        private byte[] depMaskBuffer = null;

        // 画面に表示するビットマップ
        private RenderTargetBitmap bmpBuffer = null;

        // 顔のビットマップイメージ
        private BitmapImage maskImage = null;

        // 吹き出しのビットマップイメージ
        private BitmapImage fukidashiImage = null;

        // 音源の角度
        private double soundDir = double.NaN;

        // RGB カメラの解像度，フレームレート
        private const ColorImageFormat rgbFormat = ColorImageFormat.RgbResolution640x480Fps30;

        //深度センサーの解像度，フレームレート
        private const DepthImageFormat depthFormat = DepthImageFormat.Resolution640x480Fps30;

        // KinectSensorChooser
        private KinectSensorChooser kinectChooser = new KinectSensorChooser();

        // ビットマップへの描画用 DrawingVisual
        private DrawingVisual drawVisual = new DrawingVisual();

        // 音声認識エンジン
        private SpeechRecognitionEngine speechEngine;

        // 認識された文
        private string recognizedText = null;


        // ログ書き出しストリーム.ここに対して writer.writeLine("hogehoge") で書き出せる
        private StreamWriter writer = null;
        // -------------------------------------------------------------------------------------------------------

        // コンストラクタ
        public MainWindow()
        {
            InitializeComponent();
        }

        // 初期化処理（Kinect センサーやバッファ類の初期化）
        private void windowLoaded(object sender, RoutedEventArgs e)
        {
            // ログファイルを読み込んで書き出し準備
            try
            {
                //ファイルストリームを取得
                writer = new StreamWriter("../../logs/logdata.txt",true);
                writer.WriteLine("DATE:"+DateTime.Now.ToString());
            }
            catch(IOException)
            {
                Console.WriteLine("ログファイルが開けませんでした");
            }
            // 物体位置情報のバッファ生成
            boxBuffer = new double[boxNum][];
            for (int i=0;i<boxBuffer.Length; i++)
            {
                boxBuffer[i] = new double[boxFeaturesNum];
                for (int j=0;j<boxFeaturesNum;j++)
                {
                    // 物体未検知の場合は -1
                    boxBuffer[i][j] = -1;
                }
            }

            // 画像の読み込み
            Uri imgUri = new Uri("pack://application:,,,/images/frame.png");
            maskImage = new BitmapImage(imgUri);
            Uri fkUri = new Uri("pack://application:,,,/images/fukidashi055.png");
            fukidashiImage = new BitmapImage(fkUri);

            kinectChooser.KinectChanged += KinectChanged;
            kinectChooser.PropertyChanged += KinectPropChanged;
            kinectChooser.Start();
        }
        // kinect センサーの初期化
        private void InitKinectSensor(KinectSensor kinect)
        {
            //カラーストリームの有効化
            ColorImageStream clrStream = kinect.ColorStream;
            clrStream.Enable(rgbFormat);
            // 深度ストリームの有効化
            DepthImageStream depStream = kinect.DepthStream;
            // depStream.Enable(depthFormat); // /*TEST_DEPTHFRAME*/
            
            //骨格ストリームの有効化
            SkeletonStream skelStream = kinect.SkeletonStream;
            skelStream.Enable();

            // バッファの初期化
            pixelBuffer = new byte[clrStream.FramePixelDataLength];
            if (TEST_DEPTHFLAG)
            {
                depthBuffer = new short[depStream.FramePixelDataLength];
                clrPntBuffer = new ColorImagePoint[depStream.FramePixelDataLength];
                depMaskBuffer = new byte[clrStream.FramePixelDataLength];
            }
            skeletonBuffer = new Skeleton[skelStream.FrameSkeletonArrayLength];

            bmpBuffer = new RenderTargetBitmap(clrStream.FrameWidth, clrStream.FrameHeight, 96, 96, PixelFormats.Default);

            rgbimage.Source = bmpBuffer;

            // 音声認識エンジンの初期化
            speechEngine = InitSpeechEngine();

            // イベントハンドラの登録
            kinect.AllFramesReady += AllFramesReady;
            kinect.AudioSource.SoundSourceAngleChanged += SoundSourceChanged;
            speechEngine.SpeechRecognized += SpeechRecognized;

            // 近接モードに変更
            kinect.DepthStream.Range = DepthRange.Near;

            // 着席モードに変更
            kinect.SkeletonStream.TrackingMode = SkeletonTrackingMode.Seated;

            // Kinect センサーからのストリーム取得を開始
            System.IO.Stream stream = kinect.AudioSource.Start();
            var speechAudioFormat = new SpeechAudioFormatInfo(EncodingFormat.Pcm, 16000, 16, 1, 32000, 2, null);
            speechEngine.SetInputToAudioStream(stream, speechAudioFormat);
            speechEngine.RecognizeAsync(RecognizeMode.Multiple);
        }
        // SoundSourceAngleChanged イベントのハンドラ
        // (確度が一定以上の場合だけ記録)
        private void SoundSourceChanged(object sender, SoundSourceAngleChangedEventArgs e)
        {
            if (e.ConfidenceLevel>0.5)
            {
                soundDir = e.Angle;
            }
            else
            {
                soundDir = double.NaN;
            }
        }


        // FrameReady のイベントのハンドラ
        // (画像情報を取得，顔の部分にマスクを上書きして描画)
        private void AllFramesReady(object sender, AllFramesReadyEventArgs e)
        {
            KinectSensor kinect = sender as KinectSensor;

            // タイマーを更新
            CapTimer.Text = ("" + capTimer);
            if (dataFlag == true)
            {
                capTimer++;
                if (capTimer >= 300) 
                {
                    dataFlag = false;
                    capTimer = -90;
                }
            }
            using (ColorImageFrame colorFrame = e.OpenColorImageFrame())
            // using (DepthImageFrame depthFrame = e.OpenDepthImageFrame()) /*TEST_DEPTHFRAME*/
            using (SkeletonFrame skelFrame = e.OpenSkeletonFrame())
            {
                if (colorFrame != null
                    // && depthFrame != null /*TEST_DEPTHFRAME*/
                    && skelFrame != null
                    )
                {
                    // 画像情報，(深度情報，)骨格情報をバッファに保存
                    colorFrame.CopyPixelDataTo(pixelBuffer);
                    // depthFrame.CopyPixelDataTo(depthBuffer); /*TEST_DEPTHFRAME*/
                    skelFrame.CopySkeletonDataTo(skeletonBuffer);

                    // 教示者の骨格情報を取得
                    getHeadPoints(skelFrame);
                    // 物体位置を取得
                    getBoxPoints(colorFrame, null/*TEST_DEPTHFRAME*/);
                }
            }
            // ログデータを保存
            writeLog();

            // 描画
            using (ColorImageFrame imageFrame = e.OpenColorImageFrame())
            {
                if (imageFrame != null)
                {
                    fillBitmap(kinect, imageFrame);
                }
            }
        }

        // 教示者の骨格位置を更新する
        private void getHeadPoints(SkeletonFrame skelFrame)
        {
            // トラッキングできているかを判定
            bool flag = false;

            // 取得できた骨格ごとにループ
            foreach (Skeleton skeleton in skeletonBuffer)
            {
                // トラッキングできていない骨格は処理しない
                if (skeleton.TrackingState != SkeletonTrackingState.Tracked)
                {
                    continue;
                }
                Console.WriteLine("死ね");

                flag = true;
                // 教示者の骨格位置を teacherBuffer に保存
                teacherBuffer = skeleton;
            }
            // 骨格がトラッキングできていないなら teacherBuffer を null にする
            if (flag != true)
            {
                teacherBuffer = null;
            }
        }

        // 物体の画像情報と深度情報から，物体位置を取得しリストに入れて返す
        private void getBoxPoints(ColorImageFrame colorFrame, DepthImageFrame depthFrame)
        {
            for (int i = 0;i < boxBuffer.Length; i++)
            {
                for (int j=0;j<boxBuffer[0].Length; j++)
                {
                    boxBuffer[i][j] = -1;
                    // =====================================================================================
                    // 物体位置を認識するプログラムをかけ
                    //
                    // =====================================================================================
                }
            }
        }

        // ログデータを出力する
        private void writeLog()
        {
            // タイムがマイナスなら書き出さない
            if (capTimer < 0)
            {
                return;
            }
            // フレームタイムを記録
            writer.Write(capTimer + "\t>> ");
            // 教示者の骨格を書き出し
            if (teacherBuffer != null)
            {
                JointCollection joints = teacherBuffer.Joints;
                
                                writer.Write("\t," + joints[JointType.Head].Position.X + "\t, " + joints[JointType.Head].Position.Y + "\t, " + joints[JointType.Head].Position.Z);
                                writer.Write("\t, " + joints[JointType.ShoulderCenter].Position.X + "\t, " + joints[JointType.ShoulderCenter].Position.Y + "\t, " + joints[JointType.ShoulderCenter].Position.Z);
                                writer.Write("\t, " + joints[JointType.ShoulderLeft].Position.X + "\t, " + joints[JointType.ShoulderLeft].Position.Y + "\t, " + joints[JointType.ShoulderLeft].Position.Z);
                                writer.Write("\t, " + joints[JointType.ShoulderRight].Position.X + "\t, " + joints[JointType.ShoulderRight].Position.Y + "\t, " + joints[JointType.ShoulderRight].Position.Z);
                                writer.Write("\t, " + joints[JointType.ElbowLeft].Position.X + "\t, " + joints[JointType.ElbowLeft].Position.Y + "\t, " + joints[JointType.ElbowLeft].Position.Z);
                                writer.Write("\t, " + joints[JointType.ElbowRight].Position.X + "\t, " + joints[JointType.ElbowRight].Position.Y + "\t, " + joints[JointType.ElbowRight].Position.Z);
                                writer.Write("\t, " + joints[JointType.HandLeft].Position.X + "\t, " + joints[JointType.HandLeft].Position.Y + "\t, " + joints[JointType.HandLeft].Position.Z);
                                writer.Write("\t, " + joints[JointType.HandRight].Position.X + "\t, " + joints[JointType.HandRight].Position.Y + "\t, " + joints[JointType.HandRight].Position.Z);
                
                // デモ用(gnuplot用)
/*
                writer.Write(" " + joints[JointType.HandLeft].Position.X + "  " + joints[JointType.HandLeft].Position.Y + "  " + joints[JointType.HandLeft].Position.Z);
                writer.WriteLine("");
                writer.WriteLine("");
*/
            }// 物体位置を書き出し
                         if (boxBuffer != null)
                         { 
                             for (int i = 0; i < boxBuffer.Length; i++)
                             {
                                 for (int j = 0; j < boxBuffer[0].Length; j++)
                                 {
                                     writer.Write("\t," + boxBuffer[i][j]);
                                 }
                             }
                         }
             // 改行
            writer.WriteLine("");


        }

        // RGB カメラの画像情報に，顔の位置にマスクを上書きして描画する
        private void fillBitmap(KinectSensor kinect, ColorImageFrame imageFrame)
        {
            // 描画の準備
            var drawContext = drawVisual.RenderOpen();
            int frmWidth = imageFrame.Width;
            int frmHeight = imageFrame.Height;

            // カメラの画像情報から背景のビットマップを作成し描画
            var bgImg = new WriteableBitmap(frmWidth, frmHeight, 96, 96, PixelFormats.Bgr32, null);
            bgImg.WritePixels(new Int32Rect(0, 0, frmWidth, frmHeight), pixelBuffer, frmWidth * 4, 0);
            drawContext.DrawImage(bgImg, new Rect(0, 0, frmWidth, frmHeight));

            // 教示者がトラッキングできている場合，マスクを表示する
            if (teacherBuffer != null)
            {
                // 骨格の座標から画像情報の座標に変換
                SkeletonPoint headPos = teacherBuffer.Joints[JointType.Head].Position;
                ColorImagePoint headPt = kinect.CoordinateMapper.MapSkeletonPointToColorPoint(headPos, rgbFormat);

                // 距離に応じてサイズを決定
                int size = (int)(150 / headPos.Z);

                // 頭の位置に頭の向きに回転させたマスク画像を描画
                Matrix4 headMtrx = teacherBuffer.BoneOrientations[JointType.Head].AbsoluteRotation.Matrix;
                Matrix rot = new Matrix(-headMtrx.M11, headMtrx.M12,
                                           -headMtrx.M21, headMtrx.M22,
                                           headPt.X, headPt.Y);
                drawContext.PushTransform(new MatrixTransform(rot));
                Rect rect = new Rect(-size / 2, -size / 2, size, size);
                drawContext.DrawImage(maskImage, rect);
                drawContext.Pop();

                // プレイヤーの方向が音源の方向と近い場合は吹き出しを描画
                double angle = Math.Atan2(headPos.X, headPos.Z) * 180 / Math.PI;
                if (Math.Abs(soundDir - angle) < 10)
                {
                    Rect frect = new Rect(headPt.X + 32, headPt.Y - 64, 96, 64);
                    drawContext.DrawImage(fukidashiImage, frect);

                    // 音声を認識している場合はその文を吹き出しに表示
                    if (recognizedText != null)
                    {
                        var text = new FormattedText(recognizedText, CultureInfo.GetCultureInfo("ja-JP"), FlowDirection.LeftToRight, new Typeface("Verdana"), 24, Brushes.Black);
                        var pt = new Point(headPt.X + 56, headPt.Y - 48);
                        drawContext.DrawText(text, pt);
                    }
                }
            }
            // 画面に表示するビットマップに描画
            drawContext.Close();
            bmpBuffer.Render(drawVisual);

        }

        // ウィンドウの終了処理
        private void WindowClosed(object sender, EventArgs e)
        {
            if (writer != null)
            {
                writer.Close();
            }
            kinectChooser.Stop();
            Console.WriteLine("アプリケーションを終了しました");
        }
                    
        // =======================================================================================================================================================
        // === 音声認識     ======================================================================================================================================
        // =======================================================================================================================================================

        // 音声認識エンジンを初期化，文法を登録して返す
        private SpeechRecognitionEngine InitSpeechEngine()
        {
            RecognizerInfo targetRi = null;

            foreach (RecognizerInfo recognizer in SpeechRecognitionEngine.InstalledRecognizers())
            {
                if (recognizer.AdditionalInfo.ContainsKey("Kinect") 
                   && "True".Equals(recognizer.AdditionalInfo["Kinect"], StringComparison.OrdinalIgnoreCase) 
                   && "ja-JP".Equals(recognizer.Culture.Name, StringComparison.OrdinalIgnoreCase))
                {
                    targetRi = recognizer;
                    break;
                }
            }

            if (targetRi == null)
            {
                return null;
            }

            SpeechRecognitionEngine engine = new SpeechRecognitionEngine(targetRi.Id);

            // -----------------------------------------------------------------------------------------
            // 認識する単語の追加
            var words = new Choices();
            words.Add("キネクト");
            words.Add("テスト");
            // -----------------------------------------------------------------------------------------

            var grammarBuilder = new GrammarBuilder();
            grammarBuilder.Culture = targetRi.Culture;
            grammarBuilder.Append(words);
            var grammar = new Grammar(grammarBuilder);
            engine.LoadGrammar(grammar);

            return engine;
        }
        // SpeechRecognized イベントのハンドラ
        // 確度が一定以上の場合は認識された文を記録
        private void SpeechRecognized(Object sender, SpeechRecognizedEventArgs e)
        {
            if (e.Result != null && e.Result.Confidence > 0.3)
            {
                recognizedText = e.Result.Text;
            }
            else
            {
                recognizedText = null;
            }
        }

        // =======================================================================================================================================================
        // === KinectChooer   ====================================================================================================================================
        // =======================================================================================================================================================

        // Kinect センサーの挿抜イベントに対し，初期化/終了処理を呼び出す
        private void KinectChanged(Object sender, KinectChangedEventArgs args)
        {
            if (args.OldSensor != null)
            {
                UninitKinectSensor(args.OldSensor);
            }
            if (args.NewSensor != null)
            {
                InitKinectSensor(args.NewSensor);
            }
        }
        private void KinectPropChanged(Object sender, PropertyChangedEventArgs args)
        {
            if ("Status".Equals(args.PropertyName))
            {
                textBlockStatus.Text = "Status:" + kinectChooser.Status;
            }
        }

        // Kinect センサーの終了処理
        private void UninitKinectSensor(KinectSensor kinect)
        {
            kinect.AllFramesReady -= AllFramesReady;
            kinect.AudioSource.SoundSourceAngleChanged -= SoundSourceChanged;
            UninitSpeechEngine();
        }
        // 音声認識エンジンの終了処理
        private void UninitSpeechEngine()
        {
            if (speechEngine != null)
            {
                speechEngine.SpeechRecognized -= SpeechRecognized;
                speechEngine.Dispose();
                speechEngine = null;
            }
        }

        // =======================================================================================================================================================
        // === startボタン   =====================================================================================================================================
        // =======================================================================================================================================================

       // ボタンをクリックされたときのイベントハンドラ
        private void ButtonClicked(object sender, RoutedEventArgs e)
        {
            dataFlag = true;
        }
    }
}
