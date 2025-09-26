package app;

import weka.core.Instance;
import weka.core.Instances;
import weka.core.converters.ConverterUtils.DataSource;
import weka.classifiers.Classifier;
import weka.core.DenseInstance;

import java.util.Scanner;

public class Main {

    public static void main(String[] args) {
        try {
            Scanner sc = new Scanner(System.in);

            // Load trained model once
            Classifier cls = (Classifier) weka.core.SerializationHelper.read(
                "src/weka_model/telco_not_churn_pred_LMT.model"
            );

            boolean running = true;
            while (running) {
                System.out.println();
                System.out.println("======================================");
                System.out.println("         TELCO CHURN PREDICTION       ");
                System.out.println("======================================");
                System.out.println("[1] Manual entry");
                System.out.println("[2] Load dataset (ARFF/CSV)");
                System.out.println("[0] Exit");
                System.out.println("--------------------------------------");
                System.out.print("Choose Input Mode: ");

                String choice = sc.nextLine().trim();

                if (choice.equals("1")) {
                    manualEntry(cls, sc);
                } else if (choice.equals("2")) {
                    loadDataset(cls, sc);
                } else if (choice.equals("0")) {
                    System.out.println("Exiting program...");
                    running = false;
                } else {
                    System.out.println("Invalid choice. Please try again.");
                }
            }

            sc.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static void manualEntry(Classifier cls, Scanner sc) throws Exception {
        System.out.println();
        System.out.println("------------- Manual Entry Mode -------------");

        // Ask user
        System.out.print("Enter tenure (months): ");
        double tenure = Double.parseDouble(sc.nextLine());

        System.out.println("\n[Contract Type]");
        System.out.println("  [0] Month-to-month");
        System.out.println("  [1] One year");
        System.out.println("  [2] Two year");
        System.out.print("Your Contract: ");
        int contract = Integer.parseInt(sc.nextLine());

        System.out.println("\n[Tech Support]");
        System.out.println("  [0] No");
        System.out.println("  [1] Yes");
        System.out.println("  [2] No internet service");
        System.out.print("Have Tech Support: ");
        int techSupport = Integer.parseInt(sc.nextLine());

        System.out.println("\n[Online Security]");
        System.out.println("  [0] No");
        System.out.println("  [1] Yes");
        System.out.println("  [2] No internet service");
        System.out.print("Have Online Security: ");
        int onlineSecurity = Integer.parseInt(sc.nextLine());

        System.out.println("\n[Payment Method]");
        System.out.println("  [0] Electronic check");
        System.out.println("  [1] Mailed check");
        System.out.println("  [2] Bank transfer (automatic)");
        System.out.println("  [3] Credit card (automatic)");
        System.out.print("Your Payment Method: ");
        int payment = Integer.parseInt(sc.nextLine());

        // Load dataset header
        DataSource source = new DataSource("src/weka_model/Telco_Cusomer_Churn_CFS_LMT.arff");
        Instances structure = source.getStructure();
        structure.setClassIndex(structure.numAttributes() - 1);

        // Create new instance
        Instance inst = new DenseInstance(structure.numAttributes());
        inst.setDataset(structure);

        inst.setValue(0, tenure);
        inst.setValue(1, structure.attribute(1).value(contract));   // Contract
        inst.setValue(2, structure.attribute(2).value(techSupport)); // TechSupport
        inst.setValue(3, structure.attribute(3).value(onlineSecurity)); // OnlineSecurity
        inst.setValue(4, structure.attribute(4).value(payment));    // PaymentMethod

        // Predict
        double pred = cls.classifyInstance(inst);
        String prediction = structure.classAttribute().value((int) pred);

        System.out.println("\n--------------------------------------");
        if (prediction.equals("No")) {
            System.out.println(" Prediction: Customer is likely to STAY.");
        } else {
            System.out.println(" Prediction: Customer is likely to CHURN.");
        }
        System.out.println("--------------------------------------");
    }

    private static void loadDataset(Classifier cls, Scanner sc) throws Exception {
        System.out.println();
        System.out.println("------------- Dataset Mode -------------");
        System.out.print("Enter dataset path (.arff or .csv): ");
        String path = sc.nextLine();

        DataSource source = new DataSource(path);
        Instances data = source.getDataSet();

        if (data.classIndex() == -1) {
            data.setClassIndex(data.numAttributes() - 1);
        }

        // Optional: if you saved a training header, load and compare
        DataSource trainSource = new DataSource("src/weka_model/Telco_Cusomer_Churn_CFS_LMT.arff");
        Instances header = trainSource.getDataSet();
        header.setClassIndex(header.numAttributes() - 1);

        if (!data.equalHeaders(header)) {
            System.out.println(" WARNING: Dataset structure does not match training data!");
        }

        System.out.println("\n--- Predictions ---");
        for (int i = 0; i < data.numInstances(); i++) {
            double pred = cls.classifyInstance(data.instance(i));
            String prediction = data.classAttribute().value((int) pred);

            if (prediction.equals("No")) {
                System.out.printf(" Instance %-4d → STAY%n", i + 1);
            } else {
                System.out.printf(" Instance %-4d → CHURN%n", i + 1);
            }
        }
        System.out.println("--------------------------------------");
    }
}
