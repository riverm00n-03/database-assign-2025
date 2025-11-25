# admin.py
# tkinter GUI 환경에서 데이터베이스를 관리하기 위한 파일

import sys
from pathlib import Path
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import List, Dict, Any, Optional

# 프로젝트 루트 디렉토리를 sys.path에 추가 : config 파일을 불러오기 위함.
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mysql.connector import connect
from config import DB_CONFIG

# 로컬 실행 시 Docker MySQL에 연결하기 위한 설정
# Docker 컨테이너 내부에서는 'db'를 사용하고, 로컬에서는 'localhost:3307'을 사용
LOCAL_DB_CONFIG = DB_CONFIG.copy()
if LOCAL_DB_CONFIG.get('host') == 'db':
    # 로컬 실행 시 Docker MySQL에 연결 (포트 3307로 매핑됨)
    LOCAL_DB_CONFIG['host'] = 'localhost'
    LOCAL_DB_CONFIG['port'] = int(3307)  # 포트는 정수형이어야 함
elif 'port' in LOCAL_DB_CONFIG:
    # 포트가 문자열로 설정되어 있을 경우 정수로 변환
    LOCAL_DB_CONFIG['port'] = int(LOCAL_DB_CONFIG['port'])

# 테이블 목록
TABLES = [
    'student',
    'professor',
    'subject',
    'subject_schedule',
    'enrollment',
    'class_session',
    'checkin'
]

class DatabaseAdminGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WCHECK DB 관리 프로그램")
        self.root.geometry("1200x700")
        
        self.current_table = None
        self.table_data = []
        self.table_columns = []
        self.column_types = {}  # 컬럼 타입 정보
        self.row_data_map = {}  # Treeview item_id -> row_data 매핑
        
        self.setup_ui()
        self.load_table_list()
        
    def setup_ui(self):
        # 상단 프레임: 테이블 선택
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="테이블 선택:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        self.table_combo = ttk.Combobox(top_frame, state="readonly", width=20, font=("Arial", 11))
        self.table_combo.pack(side=tk.LEFT, padx=5)
        self.table_combo.bind("<<ComboboxSelected>>", self.on_table_selected)
        
        ttk.Button(top_frame, text="새로고침", command=self.refresh_data).pack(side=tk.LEFT, padx=5)
        
        # 중간 프레임: 데이터 표시
        middle_frame = ttk.Frame(self.root, padding="10")
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview와 스크롤바
        tree_frame = ttk.Frame(middle_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        # 하단 프레임: 버튼
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X)
        
        ttk.Button(bottom_frame, text="추가", command=self.add_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="수정", command=self.update_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="삭제", command=self.delete_record).pack(side=tk.LEFT, padx=5)
        
        # 관리 기능 버튼
        ttk.Separator(bottom_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Button(bottom_frame, text="DB 리셋", command=self.reset_database).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="테스트 데이터 삽입", command=self.insert_test_data).pack(side=tk.LEFT, padx=5)
        
    def load_table_list(self):
        """Combobox에 테이블 목록 로드"""
        self.table_combo['values'] = TABLES
        if TABLES:
            self.table_combo.current(0)
            self.on_table_selected()
    
    def on_table_selected(self, event=None):
        """테이블 선택 시 데이터 로드"""
        selected_table = self.table_combo.get()
        if selected_table:
            self.current_table = selected_table
            self.load_table_data()
    
    def load_table_data(self):
        """선택된 테이블의 데이터 로드 및 표시"""
        if not self.current_table:
            return
        
        try:
            with connect(**LOCAL_DB_CONFIG) as connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute("USE wcheck")
                    
                    # 컬럼 정보 가져오기 (타입 정보 포함)
                    cursor.execute(f"DESCRIBE {self.current_table}")
                    columns_info = cursor.fetchall()
                    self.table_columns = [col['Field'] for col in columns_info]
                    # 컬럼 타입 정보 저장 (타입 변환에 사용)
                    # Type과 Null 정보를 함께 저장
                    self.column_types = {}
                    for col in columns_info:
                        field_name = col['Field']
                        self.column_types[field_name] = {
                            'type': col['Type'],
                            'null': col['Null']
                        }
                    
                    # 데이터 가져오기
                    cursor.execute(f"SELECT * FROM {self.current_table}")
                    self.table_data = cursor.fetchall()
            
            # Treeview 업데이트
            self.update_treeview()
            
        except Exception as e:
            messagebox.showerror("오류", f"데이터 로드 중 오류 발생: {e}")
    
    def update_treeview(self):
        """Treeview에 데이터 표시"""
        # 기존 항목 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.table_columns:
            return
        
        # 컬럼 설정
        self.tree['columns'] = self.table_columns
        self.tree['show'] = 'headings'
        
        # 컬럼 헤더 설정
        for col in self.table_columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor=tk.W)
        
        # PRIMARY KEY 찾기
        pk_column = self.get_primary_key_column()
        
        # 데이터 삽입 (PK를 iid로 사용)
        self.row_data_map = {}  # iid -> row_data 매핑
        for row in self.table_data:
            values = [str(row.get(col, '')) if row.get(col) is not None else '' for col in self.table_columns]
            
            # PK를 iid로 사용 (enrollment는 복합 키)
            if self.current_table == 'enrollment':
                iid = f"{row.get('student_id', '')}_{row.get('subject_id', '')}"
            elif pk_column and pk_column in row:
                iid = str(row[pk_column])
            else:
                iid = ''
            
            item_id = self.tree.insert('', tk.END, iid=iid, values=values)
            self.row_data_map[item_id] = row
    
    def get_primary_key_column(self):
        """PRIMARY KEY 컬럼 찾기"""
        if not self.table_columns:
            return None
        
        # 일반적인 PK 패턴 확인
        for col in self.table_columns:
            if col.endswith('_id') or col in ['student_id', 'professor_id', 'subject_id', 
                                               'schedule_id', 'session_id', 'checkin_id']:
                return col
        
        # 첫 번째 컬럼을 기본값으로 사용
        return self.table_columns[0]
    
    def refresh_data(self):
        """데이터 새로고침"""
        if self.current_table:
            self.load_table_data()
            messagebox.showinfo("알림", "데이터가 새로고침되었습니다.")
    
    def add_record(self):
        """레코드 추가"""
        if not self.current_table:
            messagebox.showwarning("경고", "테이블을 선택해주세요.")
            return
        
        dialog = RecordDialog(self.root, self.current_table, self.table_columns, self.column_types, mode='add')
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                with connect(**LOCAL_DB_CONFIG) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("USE wcheck")
                        
                        # INSERT 쿼리 생성
                        columns = [col for col in self.table_columns if col not in ['created_at'] and dialog.result.get(col) is not None]
                        values = [dialog.result[col] for col in columns]
                        placeholders = ', '.join(['%s'] * len(values))
                        columns_str = ', '.join(columns)
                        
                        query = f"INSERT INTO {self.current_table} ({columns_str}) VALUES ({placeholders})"
                        cursor.execute(query, values)
                        connection.commit()
                
                messagebox.showinfo("성공", "레코드가 추가되었습니다.")
                self.load_table_data()
                
            except Exception as e:
                messagebox.showerror("오류", f"레코드 추가 중 오류 발생: {e}")
    
    def update_record(self):
        """레코드 수정"""
        if not self.current_table:
            messagebox.showwarning("경고", "테이블을 선택해주세요.")
            return
        
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("경고", "수정할 레코드를 선택해주세요.")
            return
        
        # 선택된 항목의 데이터 가져오기
        item_id = selected_item[0]
        if item_id not in self.row_data_map:
            messagebox.showerror("오류", "레코드 데이터를 찾을 수 없습니다.")
            return
        
        original_data = self.row_data_map[item_id]
        
        dialog = RecordDialog(self.root, self.current_table, self.table_columns, self.column_types, mode='update', initial_data=original_data)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                with connect(**LOCAL_DB_CONFIG) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("USE wcheck")
                        
                        # PRIMARY KEY 찾기
                        pk_column = self.get_primary_key_column()
                        
                        # enrollment 테이블은 복합 PRIMARY KEY 처리
                        if self.current_table == 'enrollment':
                            update_cols = [col for col in self.table_columns if col not in ['student_id', 'subject_id', 'registered_at'] and dialog.result.get(col) is not None]
                            if update_cols:
                                update_values = [dialog.result[col] for col in update_cols]
                                set_clause = ', '.join([f"{col} = %s" for col in update_cols])
                                query = f"UPDATE {self.current_table} SET {set_clause} WHERE student_id = %s AND subject_id = %s"
                                update_values.extend([original_data['student_id'], original_data['subject_id']])
                                cursor.execute(query, update_values)
                        else:
                            # UPDATE 쿼리 생성
                            update_cols = [col for col in self.table_columns if col != pk_column and col not in ['created_at'] and dialog.result.get(col) is not None]
                            update_values = [dialog.result[col] for col in update_cols]
                            set_clause = ', '.join([f"{col} = %s" for col in update_cols])
                            
                            query = f"UPDATE {self.current_table} SET {set_clause} WHERE {pk_column} = %s"
                            update_values.append(original_data[pk_column])
                            cursor.execute(query, update_values)
                        
                        connection.commit()
                
                messagebox.showinfo("성공", "레코드가 수정되었습니다.")
                self.load_table_data()
                
            except Exception as e:
                messagebox.showerror("오류", f"레코드 수정 중 오류 발생: {e}")
    
    def delete_record(self):
        """레코드 삭제"""
        if not self.current_table:
            messagebox.showwarning("경고", "테이블을 선택해주세요.")
            return
        
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("경고", "삭제할 레코드를 선택해주세요.")
            return
        
        # 확인 대화상자
        if not messagebox.askyesno("확인", "정말로 이 레코드를 삭제하시겠습니까?"):
            return
        
        # 선택된 항목의 데이터 가져오기
        item_id = selected_item[0]
        if item_id not in self.row_data_map:
            messagebox.showerror("오류", "레코드 데이터를 찾을 수 없습니다.")
            return
        
        original_data = self.row_data_map[item_id]
        
        try:
            with connect(**LOCAL_DB_CONFIG) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("USE wcheck")
                    
                    # PRIMARY KEY 찾기
                    pk_column = self.get_primary_key_column()
                    
                    # enrollment 테이블은 복합 PRIMARY KEY 처리
                    if self.current_table == 'enrollment':
                        query = f"DELETE FROM {self.current_table} WHERE student_id = %s AND subject_id = %s"
                        cursor.execute(query, (original_data['student_id'], original_data['subject_id']))
                    else:
                        # DELETE 쿼리 실행
                        query = f"DELETE FROM {self.current_table} WHERE {pk_column} = %s"
                        cursor.execute(query, (original_data[pk_column],))
                    
                    connection.commit()
            
            messagebox.showinfo("성공", "레코드가 삭제되었습니다.")
            self.load_table_data()
            
        except Exception as e:
            messagebox.showerror("오류", f"레코드 삭제 중 오류 발생: {e}")
    
    def reset_database(self):
        """데이터베이스 리셋"""
        if not messagebox.askyesno("확인", "정말로 데이터베이스를 리셋하시겠습니까?\n모든 데이터가 삭제됩니다."):
            return
        
        try:
            reset_database()
            messagebox.showinfo("성공", "데이터베이스가 리셋되었습니다.")
            self.load_table_data()
        except Exception as e:
            messagebox.showerror("오류", f"데이터베이스 리셋 중 오류 발생: {e}")
    
    def insert_test_data(self):
        """테스트 데이터 삽입"""
        if not messagebox.askyesno("확인", "테스트 데이터를 삽입하시겠습니까?\n기존 데이터가 삭제됩니다."):
            return
        
        try:
            result = test_database()
            if result == 0:
                messagebox.showinfo("성공", "테스트 데이터가 삽입되었습니다.")
                self.load_table_data()
            else:
                messagebox.showerror("오류", "테스트 데이터 삽입에 실패했습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"테스트 데이터 삽입 중 오류 발생: {e}")


class RecordDialog:
    """레코드 추가/수정을 위한 다이얼로그"""
    def __init__(self, parent, table_name, columns, column_types, mode='add', initial_data=None):
        self.result = None
        self.table_name = table_name
        self.columns = columns
        self.column_types = column_types or {}
        self.mode = mode
        self.initial_data = initial_data or {}
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{'수정' if mode == 'update' else '추가'} - {table_name}")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.entries = {}
        self.setup_ui()
    
    def setup_ui(self):
        # 스크롤 가능한 프레임
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 입력 필드 생성
        for col in self.columns:
            # 자동 생성 컬럼은 제외
            if col in ['created_at', 'registered_at']:
                continue
            
            # enrollment 테이블 수정 모드에서 student_id, subject_id는 읽기 전용
            if self.table_name == 'enrollment' and self.mode == 'update' and col in ['student_id', 'subject_id']:
                ttk.Label(scrollable_frame, text=f"{col} (읽기 전용):").pack(anchor=tk.W, padx=10, pady=5)
                entry = ttk.Entry(scrollable_frame, width=50, state='readonly')
                entry.insert(0, initial_value if self.mode == 'update' and col in self.initial_data else "")
                entry.pack(anchor=tk.W, padx=10, pady=5)
                self.entries[col] = entry
                continue
            
            ttk.Label(scrollable_frame, text=f"{col}:").pack(anchor=tk.W, padx=10, pady=5)
            
            # 초기값 설정
            initial_value = ""
            if self.mode == 'update' and col in self.initial_data:
                initial_value = str(self.initial_data[col]) if self.initial_data[col] is not None else ""
            
            # ENUM 타입이나 특정 컬럼은 Combobox 사용
            if col == 'day_of_week':
                entry = ttk.Combobox(scrollable_frame, state="readonly", width=50)
                entry['values'] = ('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN')
                if initial_value:
                    entry.set(initial_value)
            elif col == 'status':
                entry = ttk.Combobox(scrollable_frame, state="readonly", width=50)
                entry['values'] = ('PRESENT', 'LATE', 'ABSENT')
                if initial_value:
                    entry.set(initial_value)
            elif col.endswith('_id') and self.mode == 'add':
                # 외래키는 수정 모드에서만 표시
                entry = ttk.Entry(scrollable_frame, width=50)
                entry.insert(0, initial_value)
            elif col == 'is_cancelled':
                entry = ttk.Combobox(scrollable_frame, state="readonly", width=50)
                entry['values'] = ('0', '1', 'False', 'True')
                if initial_value:
                    entry.set(str(initial_value))
            else:
                entry = ttk.Entry(scrollable_frame, width=50)
                entry.insert(0, initial_value)
            
            entry.pack(anchor=tk.W, padx=10, pady=5)
            self.entries[col] = entry
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 버튼 프레임
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="확인", command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="취소", command=self.on_cancel).pack(side=tk.RIGHT, padx=5)
    
    def on_ok(self):
        """확인 버튼 클릭"""
        self.result = {}
        
        for col, entry in self.entries.items():
            value = entry.get().strip()
            
            # 컬럼 타입 정보 가져오기
            col_info = self.column_types.get(col, {})
            col_type = col_info.get('type', '').upper() if isinstance(col_info, dict) else str(col_info).upper()
            is_nullable = col_info.get('null', 'YES') == 'YES' if isinstance(col_info, dict) else True
            
            # 빈 값 처리
            if not value:
                # NULL 가능한 필드는 None으로 설정
                if is_nullable:
                    self.result[col] = None
                    continue
                elif self.mode == 'add':
                    # 필수 필드는 빈 값일 때 건너뛰지 않음 (DB에서 처리)
                    pass
            
            # 컬럼 타입에 따른 변환
            try:
                # INT 타입 (INT, INT UNSIGNED 등)
                if 'INT' in col_type or col.endswith('_id') or col in ['student_grade', 'subject_year', 'subject_semester']:
                    if value:
                        self.result[col] = int(value)
                    else:
                        self.result[col] = None
                
                # BOOLEAN 타입
                elif 'BOOLEAN' in col_type or 'TINYINT(1)' in col_type or col == 'is_cancelled':
                    if value in ('1', 'True', 'true', 'TRUE'):
                        self.result[col] = True
                    elif value in ('0', 'False', 'false', 'FALSE'):
                        self.result[col] = False
                    elif value:
                        self.result[col] = bool(int(value)) if value.isdigit() else bool(value)
                    else:
                        self.result[col] = False
                
                # TIME 타입
                elif 'TIME' in col_type and 'TIMESTAMP' not in col_type:
                    # TIME 형식: 'HH:MM:SS' 또는 'HH:MM'
                    self.result[col] = value if value else None
                
                # DATE 타입
                elif 'DATE' in col_type and 'TIMESTAMP' not in col_type:
                    # DATE 형식: 'YYYY-MM-DD'
                    self.result[col] = value if value else None
                
                # TIMESTAMP/DATETIME 타입
                elif 'TIMESTAMP' in col_type or 'DATETIME' in col_type:
                    # TIMESTAMP 형식: 'YYYY-MM-DD HH:MM:SS' 또는 현재 시간
                    self.result[col] = value if value else None
                
                # ENUM 타입
                elif 'ENUM' in col_type:
                    # ENUM 값은 그대로 전달
                    self.result[col] = value if value else None
                
                # VARCHAR, TEXT 등 문자열 타입
                else:
                    self.result[col] = value if value else None
                    
            except ValueError as e:
                messagebox.showerror("오류", f"{col}의 값 형식이 올바르지 않습니다: {e}")
                return
        
        self.dialog.destroy()
    
    def on_cancel(self):
        """취소 버튼 클릭"""
        self.result = None
        self.dialog.destroy()


# 데이터베이스 리셋 함수
def reset_database():
    try:
        with connect(**LOCAL_DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                # wcheck 데이터베이스 사용
                cursor.execute("USE wcheck")
                cursor.execute("DROP DATABASE IF EXISTS wcheck")
                cursor.execute("CREATE DATABASE wcheck")
                cursor.execute("USE wcheck")
                cursor.execute("CREATE TABLE student (student_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL, student_number VARCHAR(50) NOT NULL UNIQUE, student_major VARCHAR(100), student_grade INT UNSIGNED, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
                cursor.execute("CREATE TABLE professor (professor_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL, major VARCHAR(100), email VARCHAR(100) UNIQUE, office_location VARCHAR(100), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
                cursor.execute("CREATE TABLE subject (subject_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, professor_id INT UNSIGNED DEFAULT NULL, name VARCHAR(255) NOT NULL, subject_year INT UNSIGNED, subject_semester INT UNSIGNED, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (professor_id) REFERENCES professor(professor_id) ON DELETE SET NULL)")
                cursor.execute("CREATE TABLE subject_schedule (schedule_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, subject_id INT UNSIGNED NOT NULL, day_of_week ENUM('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN') NOT NULL, start_time TIME NOT NULL, end_time TIME NOT NULL, location VARCHAR(100), FOREIGN KEY (subject_id) REFERENCES subject(subject_id) ON DELETE CASCADE)")
                cursor.execute("CREATE TABLE enrollment (student_id INT UNSIGNED NOT NULL, subject_id INT UNSIGNED NOT NULL, registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (student_id, subject_id), FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE, FOREIGN KEY (subject_id) REFERENCES subject(subject_id) ON DELETE CASCADE)")
                cursor.execute("CREATE TABLE class_session (session_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, schedule_id INT UNSIGNED NOT NULL, class_date DATE NOT NULL, is_cancelled BOOLEAN DEFAULT FALSE, UNIQUE KEY (schedule_id, class_date), FOREIGN KEY (schedule_id) REFERENCES subject_schedule(schedule_id) ON DELETE CASCADE)")
                cursor.execute("CREATE TABLE checkin (checkin_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, session_id INT UNSIGNED NOT NULL, student_id INT UNSIGNED NOT NULL, check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, status ENUM('PRESENT', 'LATE', 'ABSENT') DEFAULT 'PRESENT', UNIQUE KEY (session_id, student_id), FOREIGN KEY (session_id) REFERENCES class_session(session_id) ON DELETE CASCADE, FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE)")
                # commit
                print("DB 리셋 완료")
                return 0;
    except Exception as e:
        print("DB 리셋 과정 중 오류 발생 : ", e)
        return 1;

# 테스트 데이터 삽입 함수
def test_database():
    try:
        # 먼저 데이터베이스 리셋
        reset_result = reset_database()
        if reset_result != 0:
            print("데이터베이스 리셋 실패")
            return 1
        
        with connect(**LOCAL_DB_CONFIG) as connection:
            with connection.cursor() as cursor:
                cursor.execute("USE wcheck")
                
                # 교수 3명 추가
                print("교수 데이터 삽입 중...")
                cursor.execute("INSERT INTO professor (name, major, email, office_location) VALUES (%s, %s, %s, %s)", 
                              ("김교수", "컴퓨터공학", "kim@university.ac.kr", "301호"))
                cursor.execute("INSERT INTO professor (name, major, email, office_location) VALUES (%s, %s, %s, %s)", 
                              ("이교수", "전자공학", "lee@university.ac.kr", "402호"))
                cursor.execute("INSERT INTO professor (name, major, email, office_location) VALUES (%s, %s, %s, %s)", 
                              ("박교수", "정보통신공학", "park@university.ac.kr", "203호"))
                
                # 학생 10명 추가
                print("학생 데이터 삽입 중...")
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("홍길동", "2021001", "컴퓨터공학", 1))
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("김철수", "2021002", "컴퓨터공학", 1))
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("이영희", "2021003", "전자공학", 2))
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("박민수", "2021004", "정보통신공학", 2))
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("최지영", "2021005", "컴퓨터공학", 3))
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("정수진", "2021006", "전자공학", 3))
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("강동현", "2021007", "정보통신공학", 4))
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("윤서연", "2021008", "컴퓨터공학", 4))
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("임태영", "2021009", "전자공학", 1))
                cursor.execute("INSERT INTO student (name, student_number, student_major, student_grade) VALUES (%s, %s, %s, %s)", 
                              ("한소미", "2021010", "정보통신공학", 2))
                
                # 과목 4개 추가
                print("과목 데이터 삽입 중...")
                cursor.execute("INSERT INTO subject (name, subject_year, subject_semester, professor_id) VALUES (%s, %s, %s, %s)", 
                              ("데이터베이스", 2025, 2, 1))
                cursor.execute("INSERT INTO subject (name, subject_year, subject_semester, professor_id) VALUES (%s, %s, %s, %s)", 
                              ("운영체제", 2025, 2, 1))
                cursor.execute("INSERT INTO subject (name, subject_year, subject_semester, professor_id) VALUES (%s, %s, %s, %s)", 
                              ("디지털회로", 2025, 2, 2))
                cursor.execute("INSERT INTO subject (name, subject_year, subject_semester, professor_id) VALUES (%s, %s, %s, %s)", 
                              ("네트워크프로그래밍", 2025, 2, 3))
                
                # 과목 스케줄 추가
                print("과목 스케줄 데이터 삽입 중...")
                cursor.execute("INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s)", 
                              (1, "MON", "09:00:00", "10:30:00", "101호"))
                cursor.execute("INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s)", 
                              (1, "WED", "09:00:00", "10:30:00", "101호"))
                cursor.execute("INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s)", 
                              (2, "TUE", "10:30:00", "12:00:00", "102호"))
                cursor.execute("INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s)", 
                              (2, "THU", "10:30:00", "12:00:00", "102호"))
                cursor.execute("INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s)", 
                              (3, "MON", "13:00:00", "14:30:00", "201호"))
                cursor.execute("INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s)", 
                              (3, "WED", "13:00:00", "14:30:00", "201호"))
                cursor.execute("INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s)", 
                              (4, "TUE", "14:30:00", "16:00:00", "202호"))
                cursor.execute("INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s)", 
                              (4, "THU", "14:30:00", "16:00:00", "202호"))
                cursor.execute("INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s)", 
                              (1, "TUE", "12:30:00", "16:00:00", "202호"))
                cursor.execute("INSERT INTO subject_schedule (subject_id, day_of_week, start_time, end_time, location) VALUES (%s, %s, %s, %s, %s)", 
                              (2, "TUE", "13:50:00", "46:00:00", "302호"))
                
                # 수강 등록 추가
                print("수강 등록 데이터 삽입 중...")
                # 학생 1-5명이 과목 1 수강
                for student_id in range(1, 6):
                    cursor.execute("INSERT INTO enrollment (student_id, subject_id) VALUES (%s, %s)", (student_id, 1))
                # 학생 3-7명이 과목 2 수강
                for student_id in range(3, 8):
                    cursor.execute("INSERT INTO enrollment (student_id, subject_id) VALUES (%s, %s)", (student_id, 2))
                # 학생 1-4, 9-10명이 과목 3 수강
                for student_id in [1, 2, 3, 4, 9, 10]:
                    cursor.execute("INSERT INTO enrollment (student_id, subject_id) VALUES (%s, %s)", (student_id, 3))
                # 학생 5-10명이 과목 4 수강
                for student_id in range(5, 11):
                    cursor.execute("INSERT INTO enrollment (student_id, subject_id) VALUES (%s, %s)", (student_id, 4))
                
                # 수업 세션 추가 (2025년 2학기: 9월 1일 ~ 11월 24일까지)
                print("수업 세션 데이터 삽입 중...")
                
                # 기준 날짜: 2025년 11월 25일
                reference_date = datetime(2025, 11, 25).date()
                semester_start = datetime(2025, 9, 1).date()
                semester_end = datetime(2025, 11, 24).date()  # 11월 24일까지
                
                # 스케줄별 요일 매핑
                schedule_weekdays = {
                    1: 0,  # 월요일 (MON)
                    2: 2,  # 수요일 (WED)
                    3: 1,  # 화요일 (TUE)
                    4: 3,  # 목요일 (THU)
                    5: 0,  # 월요일 (MON)
                    6: 2,  # 수요일 (WED)
                    7: 1,  # 화요일 (TUE)
                    8: 3,  # 목요일 (THU)
                }
                
                session_id_counter = 1
                all_sessions = []  # (schedule_id, class_date, is_cancelled) 튜플 리스트
                
                # 각 스케줄에 대해 9월 1일부터 11월 24일까지의 모든 수업 날짜 생성
                for schedule_id in range(1, 9):
                    weekday = schedule_weekdays[schedule_id]
                    current_date = semester_start
                    
                    # 첫 번째 해당 요일 찾기
                    days_ahead = weekday - current_date.weekday()
                    if days_ahead < 0:
                        days_ahead += 7
                    first_class_date = current_date + timedelta(days=days_ahead)
                    
                    # 11월 24일까지 매주 해당 요일에 수업 세션 생성
                    class_date = first_class_date
                    while class_date <= semester_end:
                        # 휴강 처리: 각 과목별로 특정 날짜 휴강
                        is_cancelled = False
                        if schedule_id in [1, 2] and class_date == datetime(2025, 10, 6).date():  # 과목 1: 10월 6일 휴강
                            is_cancelled = True
                        elif schedule_id in [3, 4] and class_date == datetime(2025, 10, 7).date():  # 과목 2: 10월 7일 휴강
                            is_cancelled = True
                        elif schedule_id in [5, 6] and class_date == datetime(2025, 10, 13).date():  # 과목 3: 10월 13일 휴강
                            is_cancelled = True
                        
                        cursor.execute(
                            "INSERT INTO class_session (schedule_id, class_date, is_cancelled) VALUES (%s, %s, %s)",
                            (schedule_id, class_date, is_cancelled)
                        )
                        session_id = cursor.lastrowid
                        all_sessions.append((session_id, schedule_id, class_date, is_cancelled))
                        session_id_counter += 1
                        
                        class_date += timedelta(days=7)  # 다음 주 같은 요일
                
                print(f"총 {len(all_sessions)}개의 수업 세션이 생성되었습니다.")
                
                # 출석 정보 추가 (11월 24일까지의 모든 수업에 대해)
                print("출석 데이터 삽입 중...")
                
                # 수강생 정보: 각 과목별 수강생 리스트
                enrolled_students = {
                    1: list(range(1, 6)),      # 과목 1: 학생 1-5
                    2: list(range(3, 8)),      # 과목 2: 학생 3-7
                    3: [1, 2, 3, 4, 9, 10],   # 과목 3: 학생 1-4, 9-10
                    4: list(range(5, 11)),     # 과목 4: 학생 5-10
                }
                
                # 스케줄 ID -> 과목 ID 매핑
                schedule_to_subject = {
                    1: 1, 2: 1,  # 과목 1
                    3: 2, 4: 2,  # 과목 2
                    5: 3, 6: 3,  # 과목 3
                    7: 4, 8: 4,  # 과목 4
                }
                
                checkin_count = 0
                
                # 각 세션에 대해 출석 데이터 생성
                for session_id, schedule_id, class_date, is_cancelled in all_sessions:
                    subject_id = schedule_to_subject[schedule_id]
                    students = enrolled_students[subject_id]
                    
                    # 휴강인 경우 모든 학생을 출석 처리 (휴강은 출석으로 간주)
                    if is_cancelled:
                        for student_id in students:
                            cursor.execute(
                                "INSERT INTO checkin (session_id, student_id, status) VALUES (%s, %s, %s)",
                                (session_id, student_id, "PRESENT")
                            )
                            checkin_count += 1
                    else:
                        # 일반 수업: 다양한 출석 패턴 적용
                        week_number = (class_date - semester_start).days // 7 + 1
                        day_of_week = class_date.weekday()  # 0=월요일, 1=화요일, 2=수요일, 3=목요일
                        is_monday_or_wednesday = (day_of_week == 0 or day_of_week == 2)  # 월요일 또는 수요일
                        
                        # 과목별, 주차별, 요일별로 다른 출석 패턴 적용
                        if subject_id == 1:  # 데이터베이스 (월/수)
                            for idx, student_id in enumerate(students):
                                status = "PRESENT"
                                
                                # 월요일 패턴
                                if day_of_week == 0:  # 월요일
                                    if week_number == 1 and idx == 0:
                                        status = "LATE"
                                    elif week_number == 2 and idx == len(students) - 1:
                                        status = "ABSENT"
                                    elif week_number == 3 and idx == len(students) // 2:
                                        status = "LATE"
                                    elif week_number == 4 and (idx == 0 or idx == len(students) - 1):
                                        status = "LATE"
                                    elif week_number == 5 and idx == 1:
                                        status = "ABSENT"
                                    elif week_number == 6 and idx == len(students) - 2:
                                        status = "LATE"
                                    elif week_number == 7 and idx == 0:
                                        status = "ABSENT"
                                    elif week_number == 8:
                                        if idx == len(students) // 2:
                                            status = "ABSENT"
                                        elif idx == len(students) - 1:
                                            status = "LATE"
                                    elif week_number == 9 and (idx == 0 or idx == 2):
                                        status = "LATE"
                                    elif week_number == 10 and idx == len(students) - 1:
                                        status = "ABSENT"
                                    elif week_number == 11 and (idx == 1 or idx == len(students) - 2):
                                        status = "LATE"
                                    elif week_number == 12 and idx == len(students) // 2:
                                        status = "ABSENT"
                                # 수요일 패턴 (다른 패턴)
                                elif day_of_week == 2:  # 수요일
                                    if week_number == 1 and idx == 1:
                                        status = "LATE"
                                    elif week_number == 2 and idx == 0:
                                        status = "ABSENT"
                                    elif week_number == 3 and (idx == 1 or idx == len(students) - 1):
                                        status = "LATE"
                                    elif week_number == 4 and idx == len(students) - 2:
                                        status = "ABSENT"
                                    elif week_number == 5 and (idx == 0 or idx == len(students) - 1):
                                        status = "LATE"
                                    elif week_number == 6 and idx == 2:
                                        status = "ABSENT"
                                    elif week_number == 7 and idx == len(students) - 1:
                                        status = "LATE"
                                    elif week_number == 8 and idx == 1:
                                        status = "ABSENT"
                                    elif week_number == 9 and idx == len(students) // 2:
                                        status = "LATE"
                                    elif week_number == 10 and (idx == 0 or idx == len(students) - 2):
                                        status = "ABSENT"
                                    elif week_number == 11 and idx == len(students) - 1:
                                        status = "LATE"
                                    elif week_number == 12 and (idx == 1 or idx == 2):
                                        status = "ABSENT"
                                
                                cursor.execute(
                                    "INSERT INTO checkin (session_id, student_id, status) VALUES (%s, %s, %s)",
                                    (session_id, student_id, status)
                                )
                                checkin_count += 1
                        
                        elif subject_id == 2:  # 운영체제 (화/목)
                            for idx, student_id in enumerate(students):
                                status = "PRESENT"
                                
                                # 화요일 패턴
                                if day_of_week == 1:  # 화요일
                                    if week_number == 1 and idx == len(students) - 1:
                                        status = "LATE"
                                    elif week_number == 2 and idx == 0:
                                        status = "ABSENT"
                                    elif week_number == 3 and idx == len(students) - 2:
                                        status = "LATE"
                                    elif week_number == 4 and idx == 1:
                                        status = "ABSENT"
                                    elif week_number == 5 and (idx == 0 or idx == len(students) - 1):
                                        status = "LATE"
                                    elif week_number == 6 and idx == len(students) // 2:
                                        status = "ABSENT"
                                    elif week_number == 7 and idx == 2:
                                        status = "LATE"
                                    elif week_number == 8 and idx == len(students) - 1:
                                        status = "ABSENT"
                                    elif week_number == 9 and (idx == 1 or idx == len(students) - 2):
                                        status = "LATE"
                                    elif week_number == 10 and idx == 0:
                                        status = "ABSENT"
                                    elif week_number == 11 and idx == len(students) // 2:
                                        status = "LATE"
                                    elif week_number == 12 and idx == len(students) - 1:
                                        status = "ABSENT"
                                # 목요일 패턴 (다른 패턴)
                                elif day_of_week == 3:  # 목요일
                                    if week_number == 1 and idx == 0:
                                        status = "ABSENT"
                                    elif week_number == 2 and (idx == 1 or idx == len(students) - 1):
                                        status = "LATE"
                                    elif week_number == 3 and idx == len(students) // 2:
                                        status = "ABSENT"
                                    elif week_number == 4 and idx == 0:
                                        status = "LATE"
                                    elif week_number == 5 and idx == len(students) - 2:
                                        status = "ABSENT"
                                    elif week_number == 6 and (idx == 0 or idx == len(students) - 1):
                                        status = "LATE"
                                    elif week_number == 7 and idx == 1:
                                        status = "ABSENT"
                                    elif week_number == 8 and idx == len(students) - 1:
                                        status = "LATE"
                                    elif week_number == 9 and idx == 2:
                                        status = "ABSENT"
                                    elif week_number == 10 and (idx == 0 or idx == len(students) - 2):
                                        status = "LATE"
                                    elif week_number == 11 and idx == len(students) - 1:
                                        status = "ABSENT"
                                    elif week_number == 12 and idx == len(students) // 2:
                                        status = "LATE"
                                
                                cursor.execute(
                                    "INSERT INTO checkin (session_id, student_id, status) VALUES (%s, %s, %s)",
                                    (session_id, student_id, status)
                                )
                                checkin_count += 1
                        
                        elif subject_id == 3:  # 디지털회로 (월/수)
                            for idx, student_id in enumerate(students):
                                status = "PRESENT"
                                
                                # 월요일 패턴
                                if day_of_week == 0:  # 월요일
                                    if week_number == 1 and idx == 1:
                                        status = "LATE"
                                    elif week_number == 2 and idx == len(students) - 1:
                                        status = "ABSENT"
                                    elif week_number == 3 and (idx == 0 or idx == len(students) - 1):
                                        status = "LATE"
                                    elif week_number == 4 and idx == len(students) // 2:
                                        status = "ABSENT"
                                    elif week_number == 5 and idx == 2:
                                        status = "LATE"
                                    elif week_number == 6 and idx == len(students) - 2:
                                        status = "ABSENT"
                                    elif week_number == 7 and (idx == 1 or idx == len(students) - 1):
                                        status = "LATE"
                                    elif week_number == 8 and idx == 0:
                                        status = "ABSENT"
                                    elif week_number == 9 and idx == len(students) // 2:
                                        status = "LATE"
                                    elif week_number == 10 and idx == len(students) - 1:
                                        status = "ABSENT"
                                    elif week_number == 11 and (idx == 0 or idx == 2):
                                        status = "LATE"
                                    elif week_number == 12 and idx == 1:
                                        status = "ABSENT"
                                # 수요일 패턴 (다른 패턴)
                                elif day_of_week == 2:  # 수요일
                                    if week_number == 1 and idx == 0:
                                        status = "ABSENT"
                                    elif week_number == 2 and idx == 1:
                                        status = "LATE"
                                    elif week_number == 3 and idx == len(students) - 2:
                                        status = "ABSENT"
                                    elif week_number == 4 and (idx == 0 or idx == len(students) - 1):
                                        status = "LATE"
                                    elif week_number == 5 and idx == len(students) // 2:
                                        status = "ABSENT"
                                    elif week_number == 6 and idx == 0:
                                        status = "LATE"
                                    elif week_number == 7 and idx == len(students) - 1:
                                        status = "ABSENT"
                                    elif week_number == 8 and (idx == 1 or idx == len(students) - 2):
                                        status = "LATE"
                                    elif week_number == 9 and idx == 0:
                                        status = "ABSENT"
                                    elif week_number == 10 and idx == 2:
                                        status = "LATE"
                                    elif week_number == 11 and idx == len(students) - 1:
                                        status = "ABSENT"
                                    elif week_number == 12 and (idx == 0 or idx == len(students) - 2):
                                        status = "LATE"
                                
                                cursor.execute(
                                    "INSERT INTO checkin (session_id, student_id, status) VALUES (%s, %s, %s)",
                                    (session_id, student_id, status)
                                )
                                checkin_count += 1
                        
                        elif subject_id == 4:  # 네트워크프로그래밍 (화/목)
                            for idx, student_id in enumerate(students):
                                status = "PRESENT"
                                
                                # 화요일 패턴
                                if day_of_week == 1:  # 화요일
                                    if week_number == 1 and idx == len(students) - 1:
                                        status = "ABSENT"
                                    elif week_number == 2 and idx == 0:
                                        status = "LATE"
                                    elif week_number == 3 and idx == len(students) - 2:
                                        status = "ABSENT"
                                    elif week_number == 4 and (idx == 0 or idx == len(students) - 1):
                                        status = "LATE"
                                    elif week_number == 5 and idx == len(students) // 2:
                                        status = "ABSENT"
                                    elif week_number == 6 and idx == 1:
                                        status = "LATE"
                                    elif week_number == 7 and idx == len(students) - 1:
                                        status = "ABSENT"
                                    elif week_number == 8 and (idx == 0 or idx == len(students) - 2):
                                        status = "LATE"
                                    elif week_number == 9 and idx == 2:
                                        status = "ABSENT"
                                    elif week_number == 10 and idx == len(students) - 1:
                                        status = "LATE"
                                    elif week_number == 11 and idx == len(students) // 2:
                                        status = "ABSENT"
                                    elif week_number == 12 and (idx == 1 or idx == len(students) - 1):
                                        status = "LATE"
                                # 목요일 패턴 (다른 패턴)
                                elif day_of_week == 3:  # 목요일
                                    if week_number == 1 and idx == 0:
                                        status = "LATE"
                                    elif week_number == 2 and idx == len(students) - 1:
                                        status = "ABSENT"
                                    elif week_number == 3 and (idx == 0 or idx == 1):
                                        status = "LATE"
                                    elif week_number == 4 and idx == len(students) // 2:
                                        status = "ABSENT"
                                    elif week_number == 5 and idx == len(students) - 2:
                                        status = "LATE"
                                    elif week_number == 6 and (idx == 0 or idx == len(students) - 1):
                                        status = "ABSENT"
                                    elif week_number == 7 and idx == 1:
                                        status = "LATE"
                                    elif week_number == 8 and idx == len(students) - 1:
                                        status = "ABSENT"
                                    elif week_number == 9 and (idx == 0 or idx == len(students) - 2):
                                        status = "LATE"
                                    elif week_number == 10 and idx == 2:
                                        status = "ABSENT"
                                    elif week_number == 11 and idx == len(students) - 1:
                                        status = "LATE"
                                    elif week_number == 12 and idx == len(students) // 2:
                                        status = "ABSENT"
                                
                                cursor.execute(
                                    "INSERT INTO checkin (session_id, student_id, status) VALUES (%s, %s, %s)",
                                    (session_id, student_id, status)
                                )
                                checkin_count += 1
                
                print(f"총 {checkin_count}개의 출석 기록이 생성되었습니다.")
                
                connection.commit()
                print("테스트 데이터 삽입 완료")
                return 0
    except Exception as e:
        print("테스트 데이터 삽입 과정 중 오류 발생: ", e)
        return 1


def main():
    root = tk.Tk()
    app = DatabaseAdminGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
