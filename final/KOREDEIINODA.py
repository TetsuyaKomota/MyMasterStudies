import GenerateModelwithMakerMotions as generator
import EncodeModelwithSOINN as encoder
import ParsingModelwithNPYLM as parser
import PrunningModel as prunner
import MatchingModelwithNN as matcher

if __name__ == "__main__":

    dillpath = "test/"
    step = 5
    soinnN = 5000000
    soinnE = 100
    LEN = 2
    PAR_n_iter = 200
    MAT_n_iter = 10
 
    print("+--------")
    generator.generate("tmp/log/", 1000)
    print("++-------")
    generator.generate("tmp/log_test/", 100)
    print("+++------")
    encoder.predict(dillpath, "tmp/log/"step, soinnN, soinnE)
    print("++++-----")
    encoder.predict(dillpath, "tmp/log_test/", step, soinnN, soinnE)
    print("+++++----")
    parser.parsing(dillpath, "encoded.dill"LEN, PAR_n_iter)
    print("++++++---")
    parser.parsing(dillpath, "encoded_test.dill", LEN, PAR_n_iter)
    print("+++++++--")
    prunner.prunning(dillpath)
    print("++++++++-")
    matcher.matching(dillpath, MAT_n_iter) 
    print("+++++++++")
