import GenerateModelwithMakerMotions as generator
import EncodeModelwithSOINN as encoder
import ParsingModelwithNPYLM as parser
import PrunningModel as prunner
import MatchingModelwithNN as matcher

if __name__ == "__main__":
    generator.generate("tmp/log/", numTrain)
    generator.generate("tmp/log_test/", numTest)
    encoder.predict("tmp/log/")
    encoder.predict("tmp/log_test/")
    parser.parsing("encoded.dill")
    parser.parsing("encoded_test.dill")
    prunner.prunning()
    matcher.matching() 
