package komota.tests;

import edu.ufl.digitalworlds.j4k.J4KSDK;

public class TestKinect extends J4KSDK{

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO 自動生成されたメソッド・スタブ
		if(System.getProperty("os.arch").toLowerCase().indexOf("64")<0)
		{
			System.out.println("WARNING: You are running a 32bit version of Java.");
			System.out.println("This may reduce significantly the performance of this application.");
			System.out.println("It is strongly adviced to exit this program and install a 64bit version of Java.\n");
		}

		TestKinect kinect = new TestKinect();
		kinect.setSeatedSkeletonTracking(true);
		kinect.start(J4KSDK.COLOR|J4KSDK.DEPTH|J4KSDK.SKELETON);
		kinect.showViewerDialog();
	}

	@Override
	public void onColorFrameEvent(byte[] arg0) {
		// TODO 自動生成されたメソッド・スタブ
		// System.out.println("Color を受け取ったよ！arg0:"+arg0.length);
	}

	@Override
	public void onDepthFrameEvent(short[] arg0, byte[] arg1, float[] arg2, float[] arg3) {
		// TODO 自動生成されたメソッド・スタブ
		// System.out.println("Depth を受け取ったよ！arg0:"+arg0.length);
/*
  		for(int i=0;i<arg0.length;i++){

			System.out.print(",  "+arg0[i]);
		}
		System.out.println();
*/
	}

	@Override
	public void onSkeletonFrameEvent(boolean[] arg0, float[] arg1, float[] arg2, byte[] arg3) {
		// TODO 自動生成されたメソッド・スタブ

		if(arg0 == null){
			System.out.println("arg0はぬる！");
		}
		if(arg1 == null){
			System.out.println("arg1はぬる！");
		}
		if(arg2 == null){
			System.out.println("arg2はぬる！");
		}
		if(arg3 == null){
			System.out.println("arg3はぬる！");
		}
		System.out.println("Skeleton を受け取ったよ！arg0:"+arg0.length+"  arg1:"+arg1.length+"  arg3:"+arg3.length);
		for(int i=0;i<arg0.length;i++){
			System.out.print(arg0[i]+" ");
		}
		System.out.println();
	}

}
