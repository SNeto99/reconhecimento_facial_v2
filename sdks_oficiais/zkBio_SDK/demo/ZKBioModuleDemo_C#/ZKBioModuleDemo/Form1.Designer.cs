
namespace ZKBioModuleDemo
{
    partial class Form1
    {
        /// <summary>
        /// 必需的设计器变量。
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// 清理所有正在使用的资源。
        /// </summary>
        /// <param name="disposing">如果应释放托管资源，为 true；否则为 false。</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows 窗体设计器生成的代码

        /// <summary>
        /// 设计器支持所需的方法 - 不要修改
        /// 使用代码编辑器修改此方法的内容。
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.cmbFps = new System.Windows.Forms.ComboBox();
            this.label5 = new System.Windows.Forms.Label();
            this.btnUVCClose = new System.Windows.Forms.Button();
            this.btnUVCOpen = new System.Windows.Forms.Button();
            this.cmbResolution = new System.Windows.Forms.ComboBox();
            this.label1 = new System.Windows.Forms.Label();
            this.groupBox2 = new System.Windows.Forms.GroupBox();
            this.button12 = new System.Windows.Forms.Button();
            this.button11 = new System.Windows.Forms.Button();
            this.button10 = new System.Windows.Forms.Button();
            this.button9 = new System.Windows.Forms.Button();
            this.button8 = new System.Windows.Forms.Button();
            this.button7 = new System.Windows.Forms.Button();
            this.button6 = new System.Windows.Forms.Button();
            this.button5 = new System.Windows.Forms.Button();
            this.button4 = new System.Windows.Forms.Button();
            this.button3 = new System.Windows.Forms.Button();
            this.button2 = new System.Windows.Forms.Button();
            this.button1 = new System.Windows.Forms.Button();
            this.textUserNum = new System.Windows.Forms.TextBox();
            this.label6 = new System.Windows.Forms.Label();
            this.chkboxPollMatchResult = new System.Windows.Forms.CheckBox();
            this.textPalmNum = new System.Windows.Forms.TextBox();
            this.textFaceNum = new System.Windows.Forms.TextBox();
            this.textUserId = new System.Windows.Forms.TextBox();
            this.label4 = new System.Windows.Forms.Label();
            this.label3 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.btnHIDClose = new System.Windows.Forms.Button();
            this.btnHIDOpen = new System.Windows.Forms.Button();
            this.textResult = new System.Windows.Forms.TextBox();
            this.textInfo = new System.Windows.Forms.TextBox();
            this.textStatus = new System.Windows.Forms.TextBox();
            this.timer1 = new System.Windows.Forms.Timer(this.components);
            this.label7 = new System.Windows.Forms.Label();
            this.label8 = new System.Windows.Forms.Label();
            this.picMatchResult = new System.Windows.Forms.PictureBox();
            this.picNIR = new System.Windows.Forms.PictureBox();
            this.picVL = new System.Windows.Forms.PictureBox();
            this.groupBox1.SuspendLayout();
            this.groupBox2.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.picMatchResult)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.picNIR)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.picVL)).BeginInit();
            this.SuspendLayout();
            // 
            // groupBox1
            // 
            this.groupBox1.Controls.Add(this.cmbFps);
            this.groupBox1.Controls.Add(this.label5);
            this.groupBox1.Controls.Add(this.btnUVCClose);
            this.groupBox1.Controls.Add(this.btnUVCOpen);
            this.groupBox1.Controls.Add(this.cmbResolution);
            this.groupBox1.Controls.Add(this.label1);
            this.groupBox1.Location = new System.Drawing.Point(4, 4);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(289, 105);
            this.groupBox1.TabIndex = 0;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "UVC";
            // 
            // cmbFps
            // 
            this.cmbFps.FormattingEnabled = true;
            this.cmbFps.Items.AddRange(new object[] {
            "25",
            "30"});
            this.cmbFps.Location = new System.Drawing.Point(100, 47);
            this.cmbFps.Name = "cmbFps";
            this.cmbFps.Size = new System.Drawing.Size(154, 20);
            this.cmbFps.TabIndex = 5;
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Location = new System.Drawing.Point(23, 52);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(29, 12);
            this.label5.TabIndex = 4;
            this.label5.Text = "fps:";
            // 
            // btnUVCClose
            // 
            this.btnUVCClose.Location = new System.Drawing.Point(170, 76);
            this.btnUVCClose.Name = "btnUVCClose";
            this.btnUVCClose.Size = new System.Drawing.Size(75, 23);
            this.btnUVCClose.TabIndex = 3;
            this.btnUVCClose.Text = "Close";
            this.btnUVCClose.UseVisualStyleBackColor = true;
            this.btnUVCClose.Click += new System.EventHandler(this.btnUVCClose_Click);
            // 
            // btnUVCOpen
            // 
            this.btnUVCOpen.Location = new System.Drawing.Point(28, 76);
            this.btnUVCOpen.Name = "btnUVCOpen";
            this.btnUVCOpen.Size = new System.Drawing.Size(75, 23);
            this.btnUVCOpen.TabIndex = 2;
            this.btnUVCOpen.Text = "Open";
            this.btnUVCOpen.UseVisualStyleBackColor = true;
            this.btnUVCOpen.Click += new System.EventHandler(this.btnUVCOpen_Click);
            // 
            // cmbResolution
            // 
            this.cmbResolution.FormattingEnabled = true;
            this.cmbResolution.Items.AddRange(new object[] {
            "480*640",
            "720*1280"});
            this.cmbResolution.Location = new System.Drawing.Point(100, 20);
            this.cmbResolution.Name = "cmbResolution";
            this.cmbResolution.Size = new System.Drawing.Size(154, 20);
            this.cmbResolution.TabIndex = 1;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(23, 25);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(71, 12);
            this.label1.TabIndex = 0;
            this.label1.Text = "Resolution:";
            // 
            // groupBox2
            // 
            this.groupBox2.Controls.Add(this.button12);
            this.groupBox2.Controls.Add(this.button11);
            this.groupBox2.Controls.Add(this.button10);
            this.groupBox2.Controls.Add(this.button9);
            this.groupBox2.Controls.Add(this.button8);
            this.groupBox2.Controls.Add(this.button7);
            this.groupBox2.Controls.Add(this.button6);
            this.groupBox2.Controls.Add(this.button5);
            this.groupBox2.Controls.Add(this.button4);
            this.groupBox2.Controls.Add(this.button3);
            this.groupBox2.Controls.Add(this.button2);
            this.groupBox2.Controls.Add(this.button1);
            this.groupBox2.Controls.Add(this.textUserNum);
            this.groupBox2.Controls.Add(this.label6);
            this.groupBox2.Controls.Add(this.chkboxPollMatchResult);
            this.groupBox2.Controls.Add(this.textPalmNum);
            this.groupBox2.Controls.Add(this.textFaceNum);
            this.groupBox2.Controls.Add(this.textUserId);
            this.groupBox2.Controls.Add(this.label4);
            this.groupBox2.Controls.Add(this.label3);
            this.groupBox2.Controls.Add(this.label2);
            this.groupBox2.Controls.Add(this.btnHIDClose);
            this.groupBox2.Controls.Add(this.btnHIDOpen);
            this.groupBox2.Location = new System.Drawing.Point(4, 105);
            this.groupBox2.Name = "groupBox2";
            this.groupBox2.Size = new System.Drawing.Size(289, 343);
            this.groupBox2.TabIndex = 1;
            this.groupBox2.TabStop = false;
            this.groupBox2.Text = "HID";
            // 
            // button12
            // 
            this.button12.Location = new System.Drawing.Point(147, 290);
            this.button12.Name = "button12";
            this.button12.Size = new System.Drawing.Size(119, 23);
            this.button12.TabIndex = 31;
            this.button12.Text = "Device Manage";
            this.button12.UseVisualStyleBackColor = true;
            this.button12.Click += new System.EventHandler(this.button12_Click);
            // 
            // button11
            // 
            this.button11.Location = new System.Drawing.Point(21, 290);
            this.button11.Name = "button11";
            this.button11.Size = new System.Drawing.Size(116, 23);
            this.button11.TabIndex = 30;
            this.button11.Text = "Snapshot";
            this.button11.UseVisualStyleBackColor = true;
            this.button11.Click += new System.EventHandler(this.button11_Click);
            // 
            // button10
            // 
            this.button10.Location = new System.Drawing.Point(147, 261);
            this.button10.Name = "button10";
            this.button10.Size = new System.Drawing.Size(119, 23);
            this.button10.TabIndex = 29;
            this.button10.Text = "Clear Att Record";
            this.button10.UseVisualStyleBackColor = true;
            this.button10.Click += new System.EventHandler(this.button10_Click);
            // 
            // button9
            // 
            this.button9.Location = new System.Drawing.Point(21, 264);
            this.button9.Name = "button9";
            this.button9.Size = new System.Drawing.Size(116, 23);
            this.button9.TabIndex = 28;
            this.button9.Text = "Get Att Record";
            this.button9.UseVisualStyleBackColor = true;
            this.button9.Click += new System.EventHandler(this.button9_Click);
            // 
            // button8
            // 
            this.button8.Location = new System.Drawing.Point(147, 235);
            this.button8.Name = "button8";
            this.button8.Size = new System.Drawing.Size(119, 23);
            this.button8.TabIndex = 27;
            this.button8.Text = "Enroll Palm";
            this.button8.UseVisualStyleBackColor = true;
            this.button8.Click += new System.EventHandler(this.button8_Click);
            // 
            // button7
            // 
            this.button7.Location = new System.Drawing.Point(21, 238);
            this.button7.Name = "button7";
            this.button7.Size = new System.Drawing.Size(116, 23);
            this.button7.TabIndex = 26;
            this.button7.Text = "Enroll Face";
            this.button7.UseVisualStyleBackColor = true;
            this.button7.Click += new System.EventHandler(this.button7_Click);
            // 
            // button6
            // 
            this.button6.Location = new System.Drawing.Point(147, 209);
            this.button6.Name = "button6";
            this.button6.Size = new System.Drawing.Size(119, 23);
            this.button6.TabIndex = 25;
            this.button6.Text = "Enroll Face(file)";
            this.button6.UseVisualStyleBackColor = true;
            this.button6.Click += new System.EventHandler(this.button6_Click);
            // 
            // button5
            // 
            this.button5.Location = new System.Drawing.Point(21, 211);
            this.button5.Name = "button5";
            this.button5.Size = new System.Drawing.Size(116, 23);
            this.button5.TabIndex = 24;
            this.button5.Text = "Clear User";
            this.button5.UseVisualStyleBackColor = true;
            this.button5.Click += new System.EventHandler(this.button5_Click);
            // 
            // button4
            // 
            this.button4.Location = new System.Drawing.Point(147, 184);
            this.button4.Name = "button4";
            this.button4.Size = new System.Drawing.Size(119, 23);
            this.button4.TabIndex = 23;
            this.button4.Text = "Delete User";
            this.button4.UseVisualStyleBackColor = true;
            this.button4.Click += new System.EventHandler(this.button4_Click);
            // 
            // button3
            // 
            this.button3.Location = new System.Drawing.Point(21, 184);
            this.button3.Name = "button3";
            this.button3.Size = new System.Drawing.Size(116, 23);
            this.button3.TabIndex = 22;
            this.button3.Text = "Get All User";
            this.button3.UseVisualStyleBackColor = true;
            this.button3.Click += new System.EventHandler(this.button3_Click);
            // 
            // button2
            // 
            this.button2.Location = new System.Drawing.Point(147, 157);
            this.button2.Name = "button2";
            this.button2.Size = new System.Drawing.Size(119, 23);
            this.button2.TabIndex = 21;
            this.button2.Text = "Get User";
            this.button2.UseVisualStyleBackColor = true;
            this.button2.Click += new System.EventHandler(this.button2_Click);
            // 
            // button1
            // 
            this.button1.Location = new System.Drawing.Point(21, 156);
            this.button1.Name = "button1";
            this.button1.Size = new System.Drawing.Size(116, 23);
            this.button1.TabIndex = 20;
            this.button1.Text = "Add User";
            this.button1.UseVisualStyleBackColor = true;
            this.button1.Click += new System.EventHandler(this.button1_Click);
            // 
            // textUserNum
            // 
            this.textUserNum.Location = new System.Drawing.Point(88, 78);
            this.textUserNum.Name = "textUserNum";
            this.textUserNum.Size = new System.Drawing.Size(166, 21);
            this.textUserNum.TabIndex = 19;
            // 
            // label6
            // 
            this.label6.AutoSize = true;
            this.label6.Location = new System.Drawing.Point(13, 81);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(59, 12);
            this.label6.TabIndex = 18;
            this.label6.Text = "User Num:";
            // 
            // chkboxPollMatchResult
            // 
            this.chkboxPollMatchResult.AutoSize = true;
            this.chkboxPollMatchResult.Location = new System.Drawing.Point(21, 319);
            this.chkboxPollMatchResult.Name = "chkboxPollMatchResult";
            this.chkboxPollMatchResult.Size = new System.Drawing.Size(126, 16);
            this.chkboxPollMatchResult.TabIndex = 17;
            this.chkboxPollMatchResult.Text = "Poll Match Result";
            this.chkboxPollMatchResult.UseVisualStyleBackColor = true;
            this.chkboxPollMatchResult.CheckedChanged += new System.EventHandler(this.chkboxPollMatchResult_CheckedChanged);
            // 
            // textPalmNum
            // 
            this.textPalmNum.Location = new System.Drawing.Point(88, 130);
            this.textPalmNum.Name = "textPalmNum";
            this.textPalmNum.Size = new System.Drawing.Size(166, 21);
            this.textPalmNum.TabIndex = 7;
            // 
            // textFaceNum
            // 
            this.textFaceNum.Location = new System.Drawing.Point(88, 104);
            this.textFaceNum.Name = "textFaceNum";
            this.textFaceNum.Size = new System.Drawing.Size(166, 21);
            this.textFaceNum.TabIndex = 6;
            // 
            // textUserId
            // 
            this.textUserId.Location = new System.Drawing.Point(88, 52);
            this.textUserId.Name = "textUserId";
            this.textUserId.Size = new System.Drawing.Size(166, 21);
            this.textUserId.TabIndex = 5;
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(13, 134);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(59, 12);
            this.label4.TabIndex = 4;
            this.label4.Text = "Palm Num:";
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(13, 107);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(59, 12);
            this.label3.TabIndex = 3;
            this.label3.Text = "Face Num:";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(13, 56);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(53, 12);
            this.label2.TabIndex = 2;
            this.label2.Text = "User Id:";
            // 
            // btnHIDClose
            // 
            this.btnHIDClose.Location = new System.Drawing.Point(170, 20);
            this.btnHIDClose.Name = "btnHIDClose";
            this.btnHIDClose.Size = new System.Drawing.Size(75, 23);
            this.btnHIDClose.TabIndex = 1;
            this.btnHIDClose.Text = "Close";
            this.btnHIDClose.UseVisualStyleBackColor = true;
            this.btnHIDClose.Click += new System.EventHandler(this.btnHIDClose_Click);
            // 
            // btnHIDOpen
            // 
            this.btnHIDOpen.Location = new System.Drawing.Point(28, 20);
            this.btnHIDOpen.Name = "btnHIDOpen";
            this.btnHIDOpen.Size = new System.Drawing.Size(75, 23);
            this.btnHIDOpen.TabIndex = 0;
            this.btnHIDOpen.Text = "Open";
            this.btnHIDOpen.UseVisualStyleBackColor = true;
            this.btnHIDOpen.Click += new System.EventHandler(this.btnHIDOpen_Click);
            // 
            // textResult
            // 
            this.textResult.Location = new System.Drawing.Point(4, 454);
            this.textResult.Multiline = true;
            this.textResult.Name = "textResult";
            this.textResult.ReadOnly = true;
            this.textResult.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.textResult.Size = new System.Drawing.Size(205, 159);
            this.textResult.TabIndex = 4;
            // 
            // textInfo
            // 
            this.textInfo.Location = new System.Drawing.Point(4, 619);
            this.textInfo.Multiline = true;
            this.textInfo.Name = "textInfo";
            this.textInfo.ReadOnly = true;
            this.textInfo.Size = new System.Drawing.Size(289, 30);
            this.textInfo.TabIndex = 5;
            // 
            // textStatus
            // 
            this.textStatus.Location = new System.Drawing.Point(4, 659);
            this.textStatus.Name = "textStatus";
            this.textStatus.ReadOnly = true;
            this.textStatus.Size = new System.Drawing.Size(1261, 21);
            this.textStatus.TabIndex = 6;
            // 
            // timer1
            // 
            this.timer1.Tick += new System.EventHandler(this.timer1_Tick);
            // 
            // label7
            // 
            this.label7.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.label7.Location = new System.Drawing.Point(782, 16);
            this.label7.Name = "label7";
            this.label7.Size = new System.Drawing.Size(1, 643);
            this.label7.TabIndex = 7;
            // 
            // label8
            // 
            this.label8.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.label8.Location = new System.Drawing.Point(295, 14);
            this.label8.Name = "label8";
            this.label8.Size = new System.Drawing.Size(1, 642);
            this.label8.TabIndex = 9;
            // 
            // picMatchResult
            // 
            this.picMatchResult.Location = new System.Drawing.Point(218, 501);
            this.picMatchResult.Name = "picMatchResult";
            this.picMatchResult.Size = new System.Drawing.Size(72, 72);
            this.picMatchResult.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom;
            this.picMatchResult.TabIndex = 8;
            this.picMatchResult.TabStop = false;
            // 
            // picNIR
            // 
            this.picNIR.Image = global::ZKBioModuleDemo.Properties.Resources._480x640;
            this.picNIR.Location = new System.Drawing.Point(785, 13);
            this.picNIR.Name = "picNIR";
            this.picNIR.Size = new System.Drawing.Size(480, 640);
            this.picNIR.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom;
            this.picNIR.TabIndex = 3;
            this.picNIR.TabStop = false;
            // 
            // picVL
            // 
            this.picVL.Image = global::ZKBioModuleDemo.Properties.Resources._480x640;
            this.picVL.Location = new System.Drawing.Point(299, 13);
            this.picVL.Name = "picVL";
            this.picVL.Size = new System.Drawing.Size(480, 640);
            this.picVL.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom;
            this.picVL.TabIndex = 2;
            this.picVL.TabStop = false;
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1277, 686);
            this.Controls.Add(this.label8);
            this.Controls.Add(this.picMatchResult);
            this.Controls.Add(this.label7);
            this.Controls.Add(this.textStatus);
            this.Controls.Add(this.textInfo);
            this.Controls.Add(this.textResult);
            this.Controls.Add(this.picNIR);
            this.Controls.Add(this.groupBox2);
            this.Controls.Add(this.groupBox1);
            this.Controls.Add(this.picVL);
            this.Name = "Form1";
            this.Text = "Form1";
            this.FormClosing += new System.Windows.Forms.FormClosingEventHandler(this.Form1_FormClosing);
            this.groupBox1.ResumeLayout(false);
            this.groupBox1.PerformLayout();
            this.groupBox2.ResumeLayout(false);
            this.groupBox2.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.picMatchResult)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.picNIR)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.picVL)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.Button btnUVCClose;
        private System.Windows.Forms.Button btnUVCOpen;
        private System.Windows.Forms.ComboBox cmbResolution;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.GroupBox groupBox2;
        private System.Windows.Forms.Button btnHIDClose;
        private System.Windows.Forms.Button btnHIDOpen;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.TextBox textPalmNum;
        private System.Windows.Forms.TextBox textFaceNum;
        private System.Windows.Forms.TextBox textUserId;
        private System.Windows.Forms.PictureBox picVL;
        private System.Windows.Forms.PictureBox picNIR;
        private System.Windows.Forms.TextBox textResult;
        private System.Windows.Forms.TextBox textInfo;
        private System.Windows.Forms.CheckBox chkboxPollMatchResult;
        private System.Windows.Forms.ComboBox cmbFps;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.Button button8;
        private System.Windows.Forms.Button button7;
        private System.Windows.Forms.Button button6;
        private System.Windows.Forms.Button button5;
        private System.Windows.Forms.Button button4;
        private System.Windows.Forms.Button button3;
        private System.Windows.Forms.Button button2;
        private System.Windows.Forms.Button button1;
        private System.Windows.Forms.TextBox textUserNum;
        private System.Windows.Forms.Label label6;
        private System.Windows.Forms.Button button12;
        private System.Windows.Forms.Button button11;
        private System.Windows.Forms.Button button10;
        private System.Windows.Forms.Button button9;
        private System.Windows.Forms.TextBox textStatus;
        private System.Windows.Forms.Timer timer1;
        private System.Windows.Forms.Label label7;
        private System.Windows.Forms.PictureBox picMatchResult;
        private System.Windows.Forms.Label label8;
    }
}

