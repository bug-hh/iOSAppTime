#ifndef PROGRESSDIALOG_H
#define PROGRESSDIALOG_H

#include <QWidget>

namespace Ui {
class ProgressDialog;
}

class ProgressDialog : public QWidget
{
    Q_OBJECT

public:
    explicit ProgressDialog(QWidget *parent = nullptr);
    ~ProgressDialog();

private:
    Ui::ProgressDialog *ui;
};

#endif // PROGRESSDIALOG_H
