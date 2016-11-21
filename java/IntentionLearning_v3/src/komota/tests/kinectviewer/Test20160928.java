package komota.tests.kinectviewer;

public class Test20160928 {

	double[][] data;

	//コンストラクタ
	Test20160928(){
		this.data = new double[3][3];
	}

	void push(double[] ds){

		if(Math.abs(ds[0] - (this.data[0][0]+this.data[1][0]+this.data[2][0])/2) > 0.2){
			System.out.println("moved 0");
		}
		if(Math.abs(ds[1] - (this.data[0][1]+this.data[1][1]+this.data[2][1])/2) > 0.2){
			System.out.println("moved 1");
		}
		if(Math.abs(ds[2] - (this.data[0][2]+this.data[1][2]+this.data[2][2])/2) > 0.2){
			System.out.println("moved 2");
		}


		for(int i=0;i<3;i++){
			this.data[2][i] = this.data[1][i];
		}
		for(int i=0;i<3;i++){
			this.data[1][i] = this.data[0][i];
		}
		for(int i=0;i<3;i++){
			this.data[0][i] = (double)ds[i];
		}

	}
}
